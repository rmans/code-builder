#!/usr/bin/env python3
"""
OverlayPaths - Dual-mode path resolver for Code Builder

Provides consistent path resolution for both overlay and standalone modes.
All new features should use this module for path resolution.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any


class OverlayPaths:
    """Dual-mode path resolver for overlay and standalone modes."""
    
    def __init__(self):
        self._mode = self._detect_mode()
        self._cb_root = self._find_cb_root()
    
    def _detect_mode(self) -> str:
        """Detect if running in overlay or standalone mode."""
        # Check for .cb directory in current or parent directories
        current = Path.cwd()
        while current != current.parent:
            if (current / '.cb').exists():
                return 'overlay'
            current = current.parent
        
        # Check environment variable
        if os.getenv('CB_MODE') == 'overlay':
            return 'overlay'
        
        return 'standalone'
    
    def _find_cb_root(self) -> Path:
        """Find the Code Builder root directory."""
        if self._mode == 'overlay':
            # In overlay mode, find the .cb directory
            current = Path.cwd()
            while current != current.parent:
                cb_dir = current / '.cb'
                if cb_dir.exists():
                    return current
                current = current.parent
            # Fallback to current directory if .cb not found
            return Path.cwd()
        else:
            # In standalone mode, find project root (look for .git)
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').exists():
                    return current
                current = current.parent
            return Path.cwd()
    
    def is_overlay_mode(self) -> bool:
        """Check if running in overlay mode."""
        return self._mode == 'overlay'
    
    def cb_root(self) -> str:
        """Get the Code Builder root directory."""
        return str(self._cb_root)
    
    def cursor_rules_dir(self) -> str:
        """Get the Cursor rules directory."""
        if self.is_overlay_mode():
            return str(self._cb_root / '.cursor' / 'rules')
        else:
            return str(self._cb_root / 'cb_docs' / 'rules')
    
    def cb_docs_dir(self) -> str:
        """Get the Code Builder docs directory."""
        if self.is_overlay_mode():
            return str(self._cb_root / 'cb_docs')
        else:
            return str(self._cb_root / 'cb_docs')
    
    def tasks_index(self) -> str:
        """Get the tasks index file path."""
        return str(self._cb_root / 'cb_docs' / 'tasks' / 'index.md')
    
    def logs_dir(self) -> str:
        """Get the logs directory."""
        if self.is_overlay_mode():
            return str(self._cb_root / '.cb' / 'logs')
        else:
            return str(self._cb_root / 'builder' / 'logs')
    
    def cache_dir(self) -> str:
        """Get the cache directory."""
        if self.is_overlay_mode():
            return str(self._cb_root / '.cb' / 'cache')
        else:
            return str(self._cb_root / 'builder' / 'cache')
    
    def engine_dir(self) -> str:
        """Get the engine directory."""
        if self.is_overlay_mode():
            return str(self._cb_root / '.cb' / 'engine')
        else:
            return str(self._cb_root / 'builder')
    
    def templates_dir(self) -> str:
        """Get the templates directory."""
        return str(self._cb_root / 'cb_docs' / 'templates')
    
    def adrs_dir(self) -> str:
        """Get the ADRs directory."""
        return str(self._cb_root / 'cb_docs' / 'adrs')
    
    def tasks_dir(self) -> str:
        """Get the tasks directory."""
        return str(self._cb_root / 'cb_docs' / 'tasks')
    
    # Backward compatibility methods
    def get_root(self) -> str:
        """Get the project root directory (backward compatibility)."""
        return self.cb_root()
    
    def get_docs_dir(self) -> str:
        """Get the documentation directory (backward compatibility)."""
        return self.cb_docs_dir()
    
    def get_cache_dir(self) -> str:
        """Get the cache directory (backward compatibility)."""
        return self.cache_dir()
    
    def get_templates_dir(self) -> str:
        """Get the templates directory (backward compatibility)."""
        return self.templates_dir()
    
    def get_rules_dir(self) -> str:
        """Get the rules directory (backward compatibility)."""
        return self.cursor_rules_dir()
    
    def get_engine_dir(self) -> str:
        """Get the engine directory (backward compatibility)."""
        return self.engine_dir()
    
    def get_doc_dirs(self) -> list:
        """Get all document directories to scan (backward compatibility)."""
        docs_dir = self.cb_docs_dir()
        return [docs_dir] if os.path.exists(docs_dir) else []
    
    def ensure_dirs(self) -> None:
        """Ensure all required directories exist (backward compatibility)."""
        self.ensure_directories()
    
    def get_mode_info(self) -> Dict[str, Any]:
        """Get comprehensive mode information."""
        return {
            'mode': self._mode,
            'is_overlay': self.is_overlay_mode(),
            'cb_root': self.cb_root(),
            'cursor_rules_dir': self.cursor_rules_dir(),
            'cb_docs_dir': self.cb_docs_dir(),
            'tasks_index': self.tasks_index(),
            'logs_dir': self.logs_dir(),
            'cache_dir': self.cache_dir(),
            'engine_dir': self.engine_dir(),
            'templates_dir': self.templates_dir(),
            'adrs_dir': self.adrs_dir(),
            'tasks_dir': self.tasks_dir()
        }
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        dirs_to_create = [
            self.cursor_rules_dir(),
            self.cb_docs_dir(),
            self.tasks_dir(),
            self.logs_dir(),
            self.cache_dir(),
            self.templates_dir(),
            self.adrs_dir()
        ]
        
        for dir_path in dirs_to_create:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate that all required paths are accessible."""
        try:
            # Check that cb_root exists and is accessible
            if not self._cb_root.exists():
                return False
            
            # Ensure directories exist
            self.ensure_directories()
            
            # Check that we can write to key directories
            test_dirs = [self.logs_dir(), self.cache_dir()]
            for test_dir in test_dirs:
                test_file = Path(test_dir) / '.test_write'
                try:
                    test_file.write_text('test')
                    test_file.unlink()
                except (OSError, PermissionError):
                    return False
            
            return True
        except Exception:
            return False


# Global instance for easy access
overlay_paths = OverlayPaths()


# Convenience functions for backward compatibility
def cb_root() -> str:
    """Get the Code Builder root directory."""
    return overlay_paths.cb_root()


def cursor_rules_dir() -> str:
    """Get the Cursor rules directory."""
    return overlay_paths.cursor_rules_dir()


def cb_docs_dir() -> str:
    """Get the Code Builder docs directory."""
    return overlay_paths.cb_docs_dir()


def tasks_index() -> str:
    """Get the tasks index file path."""
    return overlay_paths.tasks_index()


def logs_dir() -> str:
    """Get the logs directory."""
    return overlay_paths.logs_dir()


def main():
    """CLI entry point for validation."""
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        if overlay_paths.validate():
            print("✅ OverlayPaths validation successful")
            print(f"Mode: {overlay_paths._mode}")
            print(f"Root: {overlay_paths.cb_root()}")
            sys.exit(0)
        else:
            print("❌ OverlayPaths validation failed")
            sys.exit(1)
    else:
        print("Usage: python -m builder.overlay.paths validate")
        sys.exit(1)


if __name__ == '__main__':
    main()