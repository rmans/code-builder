#!/usr/bin/env python3
"""
Centralized configuration for Code Builder.

This module provides a single source of truth for all configuration values,
including file paths, directory names, and other constants.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CodeBuilderConfig:
    """Centralized configuration for Code Builder."""
    
    # Core directories
    docs_dir: str = "cb_docs"
    cache_dir: str = "builder/cache"
    templates_dir: str = "cb_docs/templates"
    rules_dir: str = "cb_docs/rules"
    adrs_dir: str = "cb_docs/adrs"
    prd_dir: str = "cb_docs/prd"
    arch_dir: str = "cb_docs/arch"
    exec_dir: str = "cb_docs/exec"
    impl_dir: str = "cb_docs/impl"
    integrations_dir: str = "cb_docs/integrations"
    tasks_dir: str = "cb_docs/tasks"
    ux_dir: str = "cb_docs/ux"
    eval_dir: str = "cb_docs/eval"
    
    # Overlay directories
    overlay_dir: str = ".cb"
    overlay_docs_dir: str = "cb_docs"
    overlay_cache_dir: str = ".cb/builder/cache"
    overlay_venv_dir: str = ".cb/venv"
    overlay_bin_dir: str = ".cb/bin"
    
    # File patterns
    master_file_pattern: str = "0000_MASTER_{}.md"
    adr_file_pattern: str = "ADR-{}.md"
    prd_file_pattern: str = "PRD-{}.md"
    arch_file_pattern: str = "ARCH-{}.md"
    exec_file_pattern: str = "EXEC-{}.md"
    impl_file_pattern: str = "IMPL-{}.md"
    integrations_file_pattern: str = "INTEGRATIONS-{}.md"
    tasks_file_pattern: str = "TASK-{}.md"
    ux_file_pattern: str = "UX-{}.md"
    
    # Environment variables
    cb_mode_env: str = "CB_MODE"
    cb_docs_dir_env: str = "CB_DOCS_DIR"
    cb_cache_dir_env: str = "CB_CACHE_DIR"
    cb_engine_dir_env: str = "CB_ENGINE_DIR"
    cb_overlay_mode_env: str = "CB_OVERLAY_MODE"
    
    # Default values
    default_mode: str = "standalone"
    default_purpose: str = "implement"
    default_feature: str = "general"
    default_token_limit: int = 8000
    
    # Cache settings
    cache_sessions_dir: str = "builder/cache/sessions"
    cache_context_dir: str = "builder/cache/context"
    cache_reports_dir: str = "builder/cache/reports"
    
    # GitHub Actions
    github_workflows_dir: str = ".github/workflows"
    github_pr_template: str = ".github/pull_request_template.md"
    
    # Package management
    requirements_file: str = "requirements.txt"
    package_json: str = "package.json"
    cspell_config: str = "cspell.json"
    
    # Test directories
    test_data_dir: str = "tests/data"
    test_results_dir: str = "tests/results"
    test_unit_dir: str = "tests/unit"
    test_integration_dir: str = "tests/integration"
    
    # Documentation
    readme_file: str = "README.md"
    builder_readme_file: str = "builder/README.md"
    
    # AI/ML Configuration
    ai_default_temp: float = 0.7
    ai_default_top_p: float = 0.9
    ai_base_temp: float = 0.6
    ai_base_top_p: float = 0.9
    ai_temp_offset: float = 0.1
    ai_top_p_offset: float = 0.1
    ai_min_temp: float = 0.1
    ai_max_temp: float = 1.0
    ai_min_top_p: float = 0.1
    ai_max_top_p: float = 1.0
    
    # Evaluation Weights
    eval_objective_weight: float = 0.7
    eval_subjective_weight: float = 0.3
    eval_default_score: float = 50.0
    eval_confidence_threshold: float = 0.5
    
    # Scoring Weights
    score_title_weight: float = 0.4
    score_tags_weight: float = 0.3
    score_content_weight: float = 0.2
    score_tech_weight: float = 0.1
    
    # Relevance Thresholds
    relevance_threshold_low: float = 0.1
    relevance_threshold_medium: float = 0.2
    
    # Context Budget Percentages
    budget_rules: float = 0.15
    budget_acceptance: float = 0.25
    budget_adr: float = 0.15
    budget_integration: float = 0.15
    budget_arch: float = 0.10
    budget_code: float = 0.20
    budget_token_factor: float = 1.3
    
    # Network Configuration
    network_poll_interval: float = 1.0
    network_timeout: float = 60.0
    network_server_host: str = "127.0.0.1"
    network_server_port: int = 5000
    
    # Version Information
    schema_version: str = "1.0"
    app_version: str = "1.0.0"
    
    # Override with environment variables if present
    def __post_init__(self):
        """Override with environment variables if present."""
        if os.getenv(self.cb_mode_env):
            self.mode = os.getenv(self.cb_mode_env)
        else:
            self.mode = self.default_mode
            
        if os.getenv(self.cb_docs_dir_env):
            self.docs_dir = os.getenv(self.cb_docs_dir_env)
            
        if os.getenv(self.cb_cache_dir_env):
            self.cache_dir = os.getenv(self.cb_cache_dir_env)
            
        if os.getenv(self.cb_engine_dir_env):
            self.engine_dir = os.getenv(self.cb_engine_dir_env)
        else:
            self.engine_dir = self.overlay_dir if self.mode == "overlay" else "."
    
    def get_doc_type_dirs(self) -> Dict[str, str]:
        """Get all document type directories."""
        return {
            'adr': self.adrs_dir,
            'prd': self.prd_dir,
            'arch': self.arch_dir,
            'exec': self.exec_dir,
            'impl': self.impl_dir,
            'integrations': self.integrations_dir,
            'tasks': self.tasks_dir,
            'ux': self.ux_dir,
            'eval': self.eval_dir,
        }
    
    def get_doc_type_patterns(self) -> Dict[str, str]:
        """Get all document type file patterns."""
        return {
            'adr': self.adr_file_pattern,
            'prd': self.prd_file_pattern,
            'arch': self.arch_file_pattern,
            'exec': self.exec_file_pattern,
            'impl': self.impl_file_pattern,
            'integrations': self.integrations_file_pattern,
            'tasks': self.tasks_file_pattern,
            'ux': self.ux_file_pattern,
        }
    
    def get_master_files(self) -> Dict[str, str]:
        """Get all master file paths."""
        doc_dirs = self.get_doc_type_dirs()
        return {
            doc_type: os.path.join(doc_dir, self.master_file_pattern.format(doc_type.upper()))
            for doc_type, doc_dir in doc_dirs.items()
        }
    
    def is_overlay_mode(self) -> bool:
        """Check if running in overlay mode."""
        return self.mode == "overlay"
    
    def get_effective_docs_dir(self) -> str:
        """Get the effective docs directory based on mode."""
        if self.is_overlay_mode():
            return self.overlay_docs_dir
        return self.docs_dir
    
    def get_effective_cache_dir(self) -> str:
        """Get the effective cache directory based on mode."""
        if self.is_overlay_mode():
            return self.overlay_cache_dir
        return self.cache_dir
    
    def get_effective_templates_dir(self) -> str:
        """Get the effective templates directory based on mode."""
        if self.is_overlay_mode():
            return os.path.join(self.overlay_docs_dir, "templates")
        return self.templates_dir
    
    def get_effective_rules_dir(self) -> str:
        """Get the effective rules directory based on mode."""
        if self.is_overlay_mode():
            return os.path.join(self.overlay_docs_dir, "rules")
        return self.rules_dir


# Global configuration instance
config = CodeBuilderConfig()


def get_config() -> CodeBuilderConfig:
    """Get the global configuration instance."""
    return config


def reload_config() -> CodeBuilderConfig:
    """Reload configuration from environment variables."""
    global config
    config = CodeBuilderConfig()
    return config


# Convenience functions for common paths
def get_docs_dir() -> str:
    """Get the documentation directory."""
    return config.get_effective_docs_dir()


def get_cache_dir() -> str:
    """Get the cache directory."""
    return config.get_effective_cache_dir()


def get_templates_dir() -> str:
    """Get the templates directory."""
    return config.get_effective_templates_dir()


def get_rules_dir() -> str:
    """Get the rules directory."""
    return config.get_effective_rules_dir()


def get_master_file_path(doc_type: str) -> str:
    """Get the master file path for a document type."""
    master_files = config.get_master_files()
    return master_files.get(doc_type, "")


def get_doc_dir(doc_type: str) -> str:
    """Get the directory for a document type."""
    doc_dirs = config.get_doc_type_dirs()
    return doc_dirs.get(doc_type, "")


def get_doc_pattern(doc_type: str) -> str:
    """Get the file pattern for a document type."""
    patterns = config.get_doc_type_patterns()
    return patterns.get(doc_type, "")


# AI/ML Configuration
def get_ai_default_temp() -> float:
    """Get the default AI temperature."""
    return config.ai_default_temp


def get_ai_default_top_p() -> float:
    """Get the default AI top-p."""
    return config.ai_default_top_p


def get_ai_base_temp() -> float:
    """Get the base AI temperature."""
    return config.ai_base_temp


def get_ai_base_top_p() -> float:
    """Get the base AI top-p."""
    return config.ai_base_top_p


def get_ai_temp_offset() -> float:
    """Get the AI temperature offset."""
    return config.ai_temp_offset


def get_ai_top_p_offset() -> float:
    """Get the AI top-p offset."""
    return config.ai_top_p_offset


def get_ai_min_temp() -> float:
    """Get the minimum AI temperature."""
    return config.ai_min_temp


def get_ai_max_temp() -> float:
    """Get the maximum AI temperature."""
    return config.ai_max_temp


def get_ai_min_top_p() -> float:
    """Get the minimum AI top-p."""
    return config.ai_min_top_p


def get_ai_max_top_p() -> float:
    """Get the maximum AI top-p."""
    return config.ai_max_top_p


# Evaluation Configuration
def get_eval_objective_weight() -> float:
    """Get the objective evaluation weight."""
    return config.eval_objective_weight


def get_eval_subjective_weight() -> float:
    """Get the subjective evaluation weight."""
    return config.eval_subjective_weight


def get_eval_default_score() -> float:
    """Get the default evaluation score."""
    return config.eval_default_score


def get_eval_confidence_threshold() -> float:
    """Get the evaluation confidence threshold."""
    return config.eval_confidence_threshold


# Scoring Configuration
def get_score_title_weight() -> float:
    """Get the title scoring weight."""
    return config.score_title_weight


def get_score_tags_weight() -> float:
    """Get the tags scoring weight."""
    return config.score_tags_weight


def get_score_content_weight() -> float:
    """Get the content scoring weight."""
    return config.score_content_weight


def get_score_tech_weight() -> float:
    """Get the technology scoring weight."""
    return config.score_tech_weight


# Relevance Configuration
def get_relevance_threshold_low() -> float:
    """Get the low relevance threshold."""
    return config.relevance_threshold_low


def get_relevance_threshold_medium() -> float:
    """Get the medium relevance threshold."""
    return config.relevance_threshold_medium


# Context Budget Configuration
def get_budget_rules() -> float:
    """Get the rules budget percentage."""
    return config.budget_rules


def get_budget_acceptance() -> float:
    """Get the acceptance budget percentage."""
    return config.budget_acceptance


def get_budget_adr() -> float:
    """Get the ADR budget percentage."""
    return config.budget_adr


def get_budget_integration() -> float:
    """Get the integration budget percentage."""
    return config.budget_integration


def get_budget_arch() -> float:
    """Get the architecture budget percentage."""
    return config.budget_arch


def get_budget_code() -> float:
    """Get the code budget percentage."""
    return config.budget_code


def get_budget_token_factor() -> float:
    """Get the token factor."""
    return config.budget_token_factor


# Network Configuration
def get_network_poll_interval() -> float:
    """Get the network poll interval."""
    return config.network_poll_interval


def get_network_timeout() -> float:
    """Get the network timeout."""
    return config.network_timeout


def get_network_server_host() -> str:
    """Get the network server host."""
    return config.network_server_host


def get_network_server_port() -> int:
    """Get the network server port."""
    return config.network_server_port


# Version Configuration
def get_schema_version() -> str:
    """Get the schema version."""
    return config.schema_version


def get_app_version() -> str:
    """Get the application version."""
    return config.app_version


# Environment detection
def detect_mode() -> str:
    """Detect the current operating mode."""
    if os.getenv(config.cb_overlay_mode_env) == "true":
        return "overlay"
    elif os.path.exists(config.overlay_dir):
        return "overlay"
    else:
        return "standalone"


# Validation
def validate_config() -> bool:
    """Validate the current configuration."""
    try:
        # Check if required directories exist or can be created
        docs_dir = get_docs_dir()
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir, exist_ok=True)
        
        cache_dir = get_cache_dir()
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
        
        return True
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False
