"""
Core functionality for the Code Builder.

This module contains the main CLI interface and core context management functionality.
"""

from .cli import cli
from .context_rules import merge_context_rules
from .context_graph import ContextGraphBuilder, ContextGraph
from .context_select import ContextSelector
from .context_budget import ContextBudgetManager

__all__ = [
    "cli",
    "merge_context_rules", 
    "ContextGraphBuilder",
    "ContextGraph",
    "ContextSelector",
    "ContextBudgetManager"
]
