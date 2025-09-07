#!/usr/bin/env python3
"""
Overlay Path Management

Simple approach: .cb/ = project copy, cb_docs/ = docs/ copy
Code runs from .cb/ and outputs to cb_docs/
"""

import os
from pathlib import Path
from typing import Optional
from builder.config.settings import get_config


class OverlayPaths:
    """Manages path resolution for overlay and standalone modes."""
    
    def __init__(self):
        self.config = get_config()
        self.cb_mode = self.config.mode
        self.cb_docs_dir = os.environ.get(self.config.cb_docs_dir_env)
        self.cb_cache_dir = os.environ.get(self.config.cb_cache_dir_env)
        self.cb_engine_dir = os.environ.get(self.config.cb_engine_dir_env)
    
    def is_overlay_mode(self) -> bool:
        """Check if we're running in overlay mode."""
        return self.cb_mode == "overlay"
    
    def get_root(self) -> str:
        """Get the project root directory."""
        if self.is_overlay_mode() and self.cb_engine_dir:
            # In overlay mode, return the .cb/ directory as the "root"
            return str(Path(self.cb_engine_dir).resolve())
        else:
            # Standalone mode - find project root
            current = os.path.abspath(os.getcwd())
            while current != os.path.dirname(current):
                if os.path.exists(os.path.join(current, '.git')):
                    return current
                current = os.path.dirname(current)
            return os.getcwd()
    
    def get_docs_dir(self) -> str:
        """Get the documentation directory."""
        if self.is_overlay_mode() and self.cb_docs_dir:
            return self.cb_docs_dir
        # Use configuration for docs directory
        return os.path.join(self.get_root(), self.config.docs_dir)
    
    def get_cache_dir(self) -> str:
        """Get the cache directory."""
        if self.is_overlay_mode() and self.cb_cache_dir:
            return self.cb_cache_dir
        return os.path.join(self.get_root(), self.config.cache_dir)
    
    def get_templates_dir(self) -> str:
        """Get the templates directory."""
        if self.is_overlay_mode() and self.cb_docs_dir:
            # Overlay mode: use cb_docs/templates
            return os.path.join(self.cb_docs_dir, 'templates')
        else:
            # Use configuration for templates directory
            return os.path.join(self.get_root(), self.config.templates_dir)
    
    def get_rules_dir(self) -> str:
        """Get the rules directory."""
        if self.is_overlay_mode() and self.cb_docs_dir:
            # Overlay mode: use cb_docs/rules
            return os.path.join(self.cb_docs_dir, 'rules')
        else:
            # Use configuration for rules directory
            return os.path.join(self.get_root(), self.config.rules_dir)
    
    def get_engine_dir(self) -> str:
        """Get the engine directory."""
        if self.is_overlay_mode() and self.cb_engine_dir:
            return self.cb_engine_dir
        return os.path.join(self.get_root(), 'builder')
    
    def get_doc_dirs(self) -> list:
        """Get all document directories to scan."""
        if self.is_overlay_mode() and self.cb_docs_dir:
            # Overlay mode: use cb_docs
            return [self.cb_docs_dir] if os.path.exists(self.cb_docs_dir) else []
        else:
            # Use configuration for docs directory
            docs_dir = os.path.join(self.get_root(), self.config.docs_dir)
            return [docs_dir] if os.path.exists(docs_dir) else []
    
    def ensure_dirs(self) -> None:
        """Ensure all required directories exist."""
        os.makedirs(self.get_docs_dir(), exist_ok=True)
        os.makedirs(self.get_cache_dir(), exist_ok=True)
        os.makedirs(self.get_templates_dir(), exist_ok=True)
    
    def get_mode_info(self) -> dict:
        """Get information about the current mode."""
        return {
            'mode': 'overlay' if self.is_overlay_mode() else 'standalone',
            'root': self.get_root(),
            'docs_dir': self.get_docs_dir(),
            'cache_dir': self.get_cache_dir(),
            'templates_dir': self.get_templates_dir(),
            'engine_dir': self.get_engine_dir(),
            'rules_dir': self.get_rules_dir(),
            'doc_dirs': self.get_doc_dirs()
        }


# Global instance for easy access
overlay_paths = OverlayPaths()