#!/usr/bin/env python3
"""
Mode Detection

This module detects whether Code Builder is running in overlay mode,
standalone mode, or if this is a new project.
"""

import os
from typing import Literal

# Import configuration system
from ..config.settings import get_config


def detect_mode() -> Literal['overlay', 'standalone', 'new']:
    """
    Detect the current mode of operation.
    
    Returns:
        'overlay': Running in overlay mode (.cb/ exists)
        'standalone': Running in standalone mode (builder/ exists)
        'new': New project (neither exists)
    """
    # Check environment variables first
    if os.getenv('CB_OVERLAY_MODE') == 'true' or os.getenv('CB_MODE') == 'overlay':
        return 'overlay'
    
    # Check for .cb directory (overlay mode)
    if os.path.exists('.cb'):
        return 'overlay'
    
    # Check for builder directory (standalone mode)
    if os.path.exists('builder'):
        return 'standalone'
    
    # Neither exists, this is a new project
    return 'new'


def set_mode_environment() -> None:
    """Set environment variables based on detected mode."""
    mode = detect_mode()
    os.environ['CB_MODE'] = mode
    
    # Use configuration system for path construction
    config = get_config()
    
    if mode == 'overlay':
        os.environ['CB_OVERLAY_MODE'] = 'true'
        os.environ['CB_DOCS_DIR'] = config.get_effective_docs_dir()
        os.environ['CB_CACHE_DIR'] = config.get_effective_cache_dir()
        os.environ['CB_ENGINE_DIR'] = config.get_effective_engine_dir()
    elif mode == 'standalone':
        os.environ['CB_OVERLAY_MODE'] = 'false'
        os.environ['CB_DOCS_DIR'] = config.get_effective_docs_dir()
        os.environ['CB_CACHE_DIR'] = config.get_effective_cache_dir()
        os.environ['CB_ENGINE_DIR'] = config.get_effective_engine_dir()
    else:  # new
        os.environ['CB_OVERLAY_MODE'] = 'false'
        # Don't set other vars for new projects


def get_mode_info() -> dict:
    """Get detailed information about the current mode."""
    mode = detect_mode()
    
    info = {
        'mode': mode,
        'is_overlay': mode == 'overlay',
        'is_standalone': mode == 'standalone',
        'is_new': mode == 'new',
        'has_cb_dir': os.path.exists('.cb'),
        'has_builder_dir': os.path.exists('builder'),
        'has_docs_dir': os.path.exists('docs'),
        'has_cb_docs_dir': os.path.exists('cb_docs'),
    }
    
    # Use configuration system for path construction
    config = get_config()
    
    if mode in ['overlay', 'standalone']:
        info.update({
            'docs_dir': config.get_effective_docs_dir(),
            'cache_dir': config.get_effective_cache_dir(),
            'engine_dir': config.get_effective_engine_dir(),
        })
    
    return info
