"""
Code Builder - AI-assisted development tools

This package provides comprehensive tools for AI-assisted software development,
including discovery, context management, evaluation, and documentation generation.
"""

# Add the builder directory to the Python path for relative imports
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import core modules
from .core.cli import cli
from .core.context_rules import merge_context_rules
from .core.context_graph import ContextGraphBuilder, ContextGraph
from .core.context_select import ContextSelector
from .core.context_budget import ContextBudgetManager

# Import discovery modules
from .discovery.engine import DiscoveryEngine
from .discovery.analyzer import CodeAnalyzer
from .discovery.synthesizer import DiscoverySynthesizer
from .discovery.validator import DiscoveryValidator
from .discovery.generators import DiscoveryGenerators

# Import evaluator modules
from .evaluators.objective import evaluate_code, evaluate_doc
from .evaluators.artifact_detector import detect_artifact_type

# Import utility modules
from .utils.cleanup_rules import ArtifactCleaner

__version__ = "1.0.0"
__all__ = [
    "cli",
    "merge_context_rules",
    "ContextGraphBuilder",
    "ContextGraph", 
    "ContextSelector",
    "ContextBudgetManager",
    "DiscoveryEngine",
    "CodeAnalyzer",
    "DiscoverySynthesizer",
    "DiscoveryValidator",
    "DiscoveryGenerators",
    "evaluate_code",
    "evaluate_doc",
    "detect_artifact_type",
    "ArtifactCleaner"
]