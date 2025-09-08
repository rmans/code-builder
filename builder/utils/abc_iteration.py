#!/usr/bin/env python3
"""
ABC Iteration System

This module provides ABC (A/B/C) iteration capabilities for testing different
approaches and selecting the best performing variant.
"""

import json
import os
import random
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from ..evaluators.objective import evaluate_code, evaluate_doc
from ..config.settings import get_config
import click


@dataclass
class IterationVariant:
    """Represents a single iteration variant."""
    name: str
    score: float
    metadata: Dict[str, Any]
    artifacts: List[str]
    created_at: datetime


@dataclass
class IterationResult:
    """Results of an ABC iteration run."""
    target: str
    rounds: int
    variants: List[IterationVariant]
    winner: Optional[IterationVariant]
    metadata: Dict[str, Any]
    created_at: datetime


class ABCIterationRunner:
    """Runs ABC iterations and evaluates variants."""
    
    def __init__(self, cache_dir: str = None):
        config = get_config()
        if cache_dir is None:
            cache_dir = config.get_effective_cache_dir()
        
        self.cache_dir = Path(cache_dir)
        self.iterations_dir = self.cache_dir / "iterations"
        self.iterations_dir.mkdir(parents=True, exist_ok=True)
        
        # Set random seed for reproducibility
        random.seed(42)
    
    def run_iteration(self, target: str, rounds: int = 5, 
                     target_type: str = "phase") -> IterationResult:
        """Run ABC iteration for a target."""
        click.echo(f"🔄 Starting ABC iteration for {target} ({rounds} rounds)")
        
        # Create iteration directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        iteration_dir = self.iterations_dir / f"{target}_{timestamp}"
        iteration_dir.mkdir(parents=True, exist_ok=True)
        
        variants = []
        
        for round_num in range(rounds):
            click.echo(f"  Round {round_num + 1}/{rounds}")
            
            # Generate variants
            variant = self._generate_variant(target, target_type, round_num, iteration_dir)
            if variant:
                variants.append(variant)
        
        # Select winner
        winner = self._select_winner(variants)
        
        # Create result
        result = IterationResult(
            target=target,
            rounds=rounds,
            variants=variants,
            winner=winner,
            metadata={
                "iteration_dir": str(iteration_dir),
                "total_variants": len(variants),
                "seed": 42
            },
            created_at=datetime.now()
        )
        
        # Save result
        self._save_result(result, iteration_dir)
        
        click.echo(f"✅ ABC iteration completed. Winner: {winner.name if winner else 'None'}")
        
        return result
    
    def _generate_variant(self, target: str, target_type: str, round_num: int, 
                         iteration_dir: Path) -> Optional[IterationVariant]:
        """Generate a single variant."""
        variant_name = f"variant_{round_num + 1}"
        variant_dir = iteration_dir / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Generate variant based on target type
            if target_type == "phase":
                artifacts = self._generate_phase_variant(target, variant_dir)
            elif target_type == "task":
                artifacts = self._generate_task_variant(target, variant_dir)
            else:
                artifacts = self._generate_general_variant(target, variant_dir)
            
            if not artifacts:
                return None
            
            # Evaluate variant
            score = self._evaluate_variant(variant_dir, artifacts)
            
            # Create variant
            variant = IterationVariant(
                name=variant_name,
                score=score,
                metadata={
                    "round": round_num + 1,
                    "target": target,
                    "target_type": target_type,
                    "artifacts_count": len(artifacts)
                },
                artifacts=artifacts,
                created_at=datetime.now()
            )
            
            return variant
            
        except Exception as e:
            click.echo(f"    ❌ Failed to generate variant {variant_name}: {e}")
            return None
    
    def _generate_phase_variant(self, phase: str, variant_dir: Path) -> List[str]:
        """Generate a variant for a specific phase."""
        artifacts = []
        
        if phase == "implementation":
            # Generate different implementation approaches
            approaches = [
                "modular_approach",
                "monolithic_approach", 
                "microservices_approach"
            ]
            approach = random.choice(approaches)
            
            # Create sample implementation files
            impl_file = variant_dir / f"implementation_{approach}.py"
            with open(impl_file, 'w', encoding='utf-8') as f:
                f.write(f"# {approach.title()} Implementation\n")
                f.write(f"# Generated for ABC iteration\n\n")
                f.write("def main():\n")
                f.write("    pass\n")
            
            artifacts.append(str(impl_file))
            
        elif phase == "testing":
            # Generate different testing strategies
            strategies = [
                "unit_focused",
                "integration_focused",
                "e2e_focused"
            ]
            strategy = random.choice(strategies)
            
            # Create sample test files
            test_file = variant_dir / f"test_{strategy}.py"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"# {strategy.title()} Testing Strategy\n")
                f.write(f"# Generated for ABC iteration\n\n")
                f.write("def test_example():\n")
                f.write("    assert True\n")
            
            artifacts.append(str(test_file))
            
        elif phase == "documentation":
            # Generate different documentation styles
            styles = [
                "minimal",
                "comprehensive",
                "tutorial_focused"
            ]
            style = random.choice(styles)
            
            # Create sample documentation
            doc_file = variant_dir / f"documentation_{style}.md"
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(f"# {style.title()} Documentation\n")
                f.write(f"# Generated for ABC iteration\n\n")
                f.write("This is a sample documentation file.\n")
            
            artifacts.append(str(doc_file))
        
        return artifacts
    
    def _generate_task_variant(self, task_id: str, variant_dir: Path) -> List[str]:
        """Generate a variant for a specific task."""
        artifacts = []
        
        # Create different task execution approaches
        approaches = [
            "sequential",
            "parallel",
            "optimized"
        ]
        approach = random.choice(approaches)
        
        # Create task execution file
        task_file = variant_dir / f"task_{task_id}_{approach}.py"
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(f"# Task {task_id} - {approach.title()} Approach\n")
            f.write(f"# Generated for ABC iteration\n\n")
            f.write("def execute_task():\n")
            f.write("    pass\n")
        
        artifacts.append(str(task_file))
        
        return artifacts
    
    def _generate_general_variant(self, target: str, variant_dir: Path) -> List[str]:
        """Generate a general variant."""
        artifacts = []
        
        # Create a simple variant file
        variant_file = variant_dir / f"variant_{target}.txt"
        with open(variant_file, 'w', encoding='utf-8') as f:
            f.write(f"# Variant for {target}\n")
            f.write(f"# Generated for ABC iteration\n\n")
            f.write("This is a sample variant file.\n")
        
        artifacts.append(str(variant_file))
        
        return artifacts
    
    def _evaluate_variant(self, variant_dir: Path, artifacts: List[str]) -> float:
        """Evaluate a variant and return its score."""
        try:
            # Evaluate code artifacts
            code_score = 0.0
            doc_score = 0.0
            
            for artifact in artifacts:
                artifact_path = Path(artifact)
                if artifact_path.exists():
                    if artifact_path.suffix in ['.py', '.js', '.ts', '.go', '.rs', '.java']:
                        # Evaluate code
                        scores = evaluate_code(str(artifact_path))
                        code_score = max(code_score, scores.get('overall', 0.0))
                    elif artifact_path.suffix in ['.md', '.rst', '.txt']:
                        # Evaluate documentation
                        scores = evaluate_doc(str(artifact_path), 'general')
                        doc_score = max(doc_score, scores.get('overall', 0.0))
            
            # Combine scores (weighted average)
            if code_score > 0 and doc_score > 0:
                return (code_score * 0.7 + doc_score * 0.3)
            elif code_score > 0:
                return code_score
            elif doc_score > 0:
                return doc_score
            else:
                # Default score based on artifact count
                return min(1.0, len(artifacts) * 0.2)
                
        except Exception as e:
            click.echo(f"    ⚠️  Evaluation error: {e}")
            return 0.5  # Default neutral score
    
    def _select_winner(self, variants: List[IterationVariant]) -> Optional[IterationVariant]:
        """Select the winning variant based on scores."""
        if not variants:
            return None
        
        # Sort by score (descending)
        sorted_variants = sorted(variants, key=lambda v: v.score, reverse=True)
        return sorted_variants[0]
    
    def _save_result(self, result: IterationResult, iteration_dir: Path) -> None:
        """Save iteration result to file."""
        result_file = iteration_dir / "iteration_result.json"
        
        # Convert to serializable format
        result_data = {
            "target": result.target,
            "rounds": result.rounds,
            "variants": [
                {
                    "name": v.name,
                    "score": v.score,
                    "metadata": v.metadata,
                    "artifacts": v.artifacts,
                    "created_at": v.created_at.isoformat()
                }
                for v in result.variants
            ],
            "winner": {
                "name": result.winner.name,
                "score": result.winner.score,
                "metadata": result.winner.metadata,
                "artifacts": result.winner.artifacts,
                "created_at": result.winner.created_at.isoformat()
            } if result.winner else None,
            "metadata": result.metadata,
            "created_at": result.created_at.isoformat()
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, default=str)
    
    def list_iterations(self) -> List[Dict[str, Any]]:
        """List all previous iterations."""
        iterations = []
        
        for iteration_dir in self.iterations_dir.iterdir():
            if iteration_dir.is_dir():
                result_file = iteration_dir / "iteration_result.json"
                if result_file.exists():
                    try:
                        with open(result_file, 'r', encoding='utf-8') as f:
                            result_data = json.load(f)
                        iterations.append({
                            "directory": str(iteration_dir),
                            "target": result_data.get("target", "unknown"),
                            "rounds": result_data.get("rounds", 0),
                            "variants": len(result_data.get("variants", [])),
                            "winner": result_data.get("winner", {}).get("name", "none"),
                            "created_at": result_data.get("created_at", "")
                        })
                    except Exception as e:
                        click.echo(f"Warning: Could not read iteration {iteration_dir}: {e}")
        
        return sorted(iterations, key=lambda x: x["created_at"], reverse=True)
    
    def get_iteration_result(self, iteration_dir: str) -> Optional[Dict[str, Any]]:
        """Get detailed result for a specific iteration."""
        result_file = Path(iteration_dir) / "iteration_result.json"
        
        if not result_file.exists():
            return None
        
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            click.echo(f"Error reading iteration result: {e}")
            return None


def create_abc_runner(cache_dir: str = None) -> ABCIterationRunner:
    """Create a new ABCIterationRunner instance."""
    return ABCIterationRunner(cache_dir)


# Global runner instance
abc_runner = create_abc_runner()


def run_abc_iteration(target: str, rounds: int = 5, target_type: str = "phase") -> IterationResult:
    """Run ABC iteration using the global runner."""
    return abc_runner.run_iteration(target, rounds, target_type)
