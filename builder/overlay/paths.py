#!/usr/bin/env python3
"""
Overlay Path Management

This module provides path resolution for the Code Builder overlay mode,
handling the dual-path system where overlay mode uses cb_docs/ and .cb/
while standalone mode uses docs/ and builder/.
"""

import os
from typing import Optional


class OverlayPaths:
    """Manages path resolution for overlay and standalone modes."""
    
    def __init__(self):
        self._root = None
        self._docs_dir = None
        self._cache_dir = None
        self._templates_dir = None
        self._engine_dir = None
    
    def get_root(self) -> str:
        """Get the project root directory."""
        if self._root is None:
            # Try to find root by looking for .git or .cb
            current = os.path.abspath(os.getcwd())
            while current != os.path.dirname(current):
                if os.path.exists(os.path.join(current, '.git')) or os.path.exists(os.path.join(current, '.cb')):
                    self._root = current
                    break
                current = os.path.dirname(current)
            else:
                # Fallback to current directory
                self._root = os.getcwd()
        return self._root
    
    def get_docs_dir(self) -> str:
        """Get the documentation directory."""
        if self._docs_dir is None:
            if self.is_overlay_mode():
                # Overlay mode: use cb_docs
                self._docs_dir = os.path.join(self.get_root(), 'cb_docs')
            else:
                # Standalone mode: use docs
                self._docs_dir = os.path.join(self.get_root(), 'docs')
        return self._docs_dir
    
    def get_cache_dir(self) -> str:
        """Get the cache directory."""
        if self._cache_dir is None:
            if self.is_overlay_mode():
                # Overlay mode: use .cb/cache
                self._cache_dir = os.path.join(self.get_root(), '.cb', 'cache')
            else:
                # Standalone mode: use builder/cache
                self._cache_dir = os.path.join(self.get_root(), 'builder', 'cache')
        return self._cache_dir
    
    def get_templates_dir(self) -> str:
        """Get the templates directory."""
        if self._templates_dir is None:
            if self.is_overlay_mode():
                # Overlay mode: prefer .cb/engine/templates, fallback to cb_docs/templates
                engine_templates = os.path.join(self.get_root(), '.cb', 'engine', 'templates')
                docs_templates = os.path.join(self.get_root(), 'cb_docs', 'templates')
                if os.path.exists(engine_templates):
                    self._templates_dir = engine_templates
                elif os.path.exists(docs_templates):
                    self._templates_dir = docs_templates
                else:
                    # Fallback to docs/templates
                    self._templates_dir = os.path.join(self.get_root(), 'docs', 'templates')
            else:
                # Standalone mode: use docs/templates
                self._templates_dir = os.path.join(self.get_root(), 'docs', 'templates')
        return self._templates_dir
    
    def get_engine_dir(self) -> str:
        """Get the engine directory."""
        if self._engine_dir is None:
            if self.is_overlay_mode():
                # Overlay mode: use .cb/engine
                self._engine_dir = os.path.join(self.get_root(), '.cb', 'engine')
            else:
                # Standalone mode: use builder
                self._engine_dir = os.path.join(self.get_root(), 'builder')
        return self._engine_dir
    
    def is_overlay_mode(self) -> bool:
        """Check if we're running in overlay mode."""
        return (
            os.getenv('CB_OVERLAY_MODE') == 'true' or
            os.getenv('CB_MODE') == 'overlay' or
            os.path.exists(os.path.join(self.get_root(), '.cb'))
        )
    
    def get_rules_dir(self) -> str:
        """Get the rules directory."""
        if self.is_overlay_mode():
            # Overlay mode: prefer .cb/engine/docs/rules, fallback to cb_docs/rules
            engine_rules = os.path.join(self.get_root(), '.cb', 'engine', 'docs', 'rules')
            docs_rules = os.path.join(self.get_root(), 'cb_docs', 'rules')
            if os.path.exists(engine_rules):
                return engine_rules
            elif os.path.exists(docs_rules):
                return docs_rules
            else:
                # Fallback to docs/rules
                return os.path.join(self.get_root(), 'docs', 'rules')
        else:
            # Standalone mode: use docs/rules
            return os.path.join(self.get_root(), 'docs', 'rules')
    
    def get_doc_dirs(self) -> list:
        """Get all document directories to scan."""
        if self.is_overlay_mode():
            # Overlay mode: prefer cb_docs, fallback to docs
            cb_docs = os.path.join(self.get_root(), 'cb_docs')
            docs = os.path.join(self.get_root(), 'docs')
            dirs = []
            if os.path.exists(cb_docs):
                dirs.append(cb_docs)
            if os.path.exists(docs):
                dirs.append(docs)
            return dirs
        else:
            # Standalone mode: use docs
            docs = os.path.join(self.get_root(), 'docs')
            return [docs] if os.path.exists(docs) else []
    
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
