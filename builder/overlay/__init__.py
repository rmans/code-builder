"""
Code Builder Overlay Module

This module provides overlay-specific functionality for the Code Builder,
including path management, mode detection, and compatibility layers.
"""

from .paths import OverlayPaths
from .mode import detect_mode

__all__ = ['OverlayPaths', 'detect_mode']
