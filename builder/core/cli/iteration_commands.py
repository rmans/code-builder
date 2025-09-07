#!/usr/bin/env python3
"""
Iteration Commands Module

This module contains iteration-related commands like iter:*, plan:*
"""

import click
import os
import json
import fnmatch
from pathlib import Path
from .base import cli, get_project_root

# Import required modules and functions
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
    DOCS = overlay_paths.get_docs_dir()
    CACHE = overlay_paths.get_cache_dir()
except ImportError:
    ROOT = get_project_root()
    DOCS = ROOT / "cb_docs"
    CACHE = ROOT / ".cb" / "cache"

def _load_rules(feature, stacks):
    """Load rules for iteration."""
    try:
        from ..context_rules import merge_context_rules
        return merge_context_rules(feature or None, [s.strip() for s in stacks.split(",") if s.strip()])
    except ImportError:
        return {"rules_markdown": "", "guardrails": {}}

def _abc_params(base_t, base_p, round_num, variant):
    """Calculate ABC parameters for iteration."""
    # Simplified ABC parameter calculation
    if variant == "A":
        return base_t, base_p
    elif variant == "B":
        return base_t + 0.1, base_p + 0.1
    else:  # C
        return base_t - 0.1, base_p - 0.1

def _analyze_iteration_context(context):
    """Analyze iteration context for learning."""
    # Simplified analysis - in real implementation this would analyze previous rounds
    return {
        "successful_patterns": ["pattern1", "pattern2"],
        "improvement_areas": ["area1", "area2"],
        "improvement_suggestions": ["suggestion1", "suggestion2"],
        "weak_metrics": {"metric1": [0.5, 0.6], "metric2": [0.4, 0.5]}
    }

def _get_baseline_params(context):
    """Get baseline parameters for iteration."""
    # Simplified baseline parameters
    return 0.7, 0.9

def generate_variants(current_file, context):
    """Generate A/B/C variants of the current file."""
    # Simplified variant generation - in real implementation this would use AI
    variants = {}
    for variant in ["A", "B", "C"]:
        variant_path = os.path.join(CACHE, f"variant_{variant}.ts")
        with open(variant_path, 'w', encoding='utf-8') as f:
            f.write(f"// Generated variant {variant}\nexport const hello = () => 'hi from {variant}';\n")
        variants[variant] = variant_path
    return variants

def _select_winner_automatically(objective_scores):
    """Automatically select winner based on objective scores."""
    return max(objective_scores.keys(), key=lambda k: objective_scores[k].get('overall', 0))

def _prompt_for_winner(objective_scores, round_num, total_rounds):
    """Prompt user to select winner."""
    click.echo(f"\nRound {round_num}/{total_rounds} - Select winner:")
    for variant, scores in objective_scores.items():
        click.echo(f"  {variant}: {scores.get('overall', 0):.1f}")
    
    while True:
        choice = click.prompt("Enter winner (A/B/C)", type=str).upper()
        if choice in objective_scores:
            return choice
        click.echo("Invalid choice. Please enter A, B, or C.")

def _apply_winner(winner_path, target_path):
    """Apply winner variant to target path."""
    with open(winner_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)

def _cleanup_variants(variant_paths):
    """Clean up variant files."""
    for path in variant_paths.values():
        if os.path.exists(path):
            os.remove(path)

def _save_iteration_history(target_path, history):
    """Save iteration history to cache."""
    os.makedirs(CACHE, exist_ok=True)
    history_path = os.path.join(CACHE, "iter_history.json")
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

def _print_iteration_summary(target_path, history):
    """Print iteration summary."""
    click.echo(f"\n🎉 Iteration complete for {target_path}")
    click.echo(f"📊 Completed {len(history)} rounds")
    if history:
        final_winner = history[-1]["winner"]
        final_score = history[-1]["objective_scores"][final_winner].get('overall', 0)
        click.echo(f"🏆 Final winner: {final_winner} (score: {final_score:.1f})")

# Iteration Commands
@cli.command("plan:sync")
@click.option("--feature", default="")
@click.option("--stacks", default="typescript,react")
def plan_sync(feature, stacks):
    """Sync planning data and build context."""
    os.makedirs(CACHE, exist_ok=True)
    rules = _load_rules(feature, stacks)
    ctx = {
        "trace": {"prd":"PRD#TBD","arch":"ARCH#TBD","ux":"UX#TBD","integration":"INT#TBD","adrs":[]},
        "acceptance": ["compiles","tests pass"],
        "goal": "Scaffolded by plan:sync",
        "name": "Scaffold",
        "feature": feature,
        "rules": rules
    }
    with open(os.path.join(CACHE,"context.json"),"w",encoding="utf-8") as f:
        json.dump(ctx, f, indent=2)
    click.echo("Wrote builder/cache/context.json")

@cli.command("plan:auto")
@click.argument("path", default="src")
@click.option("--stacks", default="typescript,react")
def plan_auto(path, stacks):
    """Infer feature from builder/feature_map.json for PATH and build context."""
    fmap = {}
    try:
        fmap = json.loads(Path("builder/feature_map.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    
    feature = ""
    for pattern, val in (fmap or {}).items():
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatchcase(path, pattern):
            feature = val
            break
    
    click.echo(f"🔍 Detected feature: '{feature or 'none'}' for path: {path}")
    
    # Call ctx:build-enhanced after feature detection
    try:
        click.echo("🔧 Building enhanced context package...")
        
        # Simplified context building - in real implementation this would use the full context system
        ctx = {
            "trace": {"prd":"PRD#TBD","arch":"ARCH#TBD","ux":"UX#TBD","integration":"INT#TBD","adrs":[]},
            "acceptance": ["compiles","tests pass"],
            "goal": f"Auto-planned for {path}",
            "name": "AutoPlan",
            "feature": feature,
            "rules": _load_rules(feature, stacks)
        }
        
        os.makedirs(CACHE, exist_ok=True)
        with open(os.path.join(CACHE,"context.json"),"w",encoding="utf-8") as f:
            json.dump(ctx, f, indent=2)
        
        click.echo("✅ Enhanced context package built")
        click.echo("Wrote builder/cache/context.json")
        
    except Exception as e:
        click.echo(f"❌ Error building context: {e}")
        return 1
    
    return 0

@cli.command("iter:run")
@click.argument("target_path")
@click.option("--rounds", default=3)
def iter_run(target_path, rounds):
    """Run ABC iteration on target path."""
    os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
    history = []
    base_t, base_p = 0.7, 0.9  # Simplified baseline parameters
    best = {"score": -1, "content": "", "params": (base_t, base_p)}
    
    for r in range(rounds):
        variants = {}
        for v in ["A","B","C"]:
            t,p = _abc_params(base_t, base_p, r, v)
            content = f"// gen variant {v} @T={t} P={p}\nexport const hello = ()=>'hi';\n"
            score = len(content) - (1 if v!='A' else 0)
            variants[v] = {"content": content, "score": score, "params": (t,p)}
        
        winner = max(variants.values(), key=lambda x: x["score"])
        base_t, base_p = winner["params"]
        best = winner
        history.append({"round": r+1, "winner": {"T":base_t,"P":base_p}, "score": winner["score"]})
    
    with open(target_path, "w", encoding="utf-8") as f: 
        f.write(best["content"])
    
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, "iter_history.json"), "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    
    click.echo(f"Finalized {target_path} with ABC loop ({rounds} rounds)")

@cli.command("iter:cursor")
@click.argument("target_path")
@click.option("--rounds", default=3, help="Number of ABC iteration rounds")
@click.option("--auto-select", is_flag=True, help="Automatically select winner based on objective scores")
def iter_cursor(target_path, rounds, auto_select):
    """Run iterative ABC evaluation with Cursor."""
    try:
        import sys
        sys.path.append(os.path.join(ROOT, "builder"))
        
        # Simplified artifact detection
        artifact_type = "code" if target_path.endswith(('.ts', '.js', '.py', '.java')) else "doc"
        current_file = target_path
        iteration_history = []
        
        click.echo(f"Starting ABC iteration with {rounds} rounds...")
        click.echo(f"Target file: {target_path}")
        click.echo(f"Artifact type: {artifact_type}")
        click.echo("="*60)
        
        for round_num in range(1, rounds + 1):
            click.echo(f"\n🔄 ROUND {round_num}/{rounds}")
            click.echo("-" * 40)
            
            # Generate variants from current file with learning context
            click.echo("Generating A/B/C variants...")
            if iteration_history:
                learning_context = _analyze_iteration_context({"rounds": iteration_history})
                click.echo(f"  Learning from {len(iteration_history)} previous rounds...")
                if learning_context.get("successful_patterns"):
                    click.echo(f"  Successful patterns: {learning_context['successful_patterns']}")
                if learning_context.get("improvement_areas"):
                    click.echo(f"  Improvement areas: {learning_context['improvement_areas']}")
            
            # Get baseline parameters for display
            baseline_temp, baseline_top_p = _get_baseline_params({"rounds": iteration_history} if iteration_history else {})
            
            click.echo("  AI Generation Parameters:")
            click.echo(f"    Baseline: temp={baseline_temp:.2f}, top_p={baseline_top_p:.2f}")
            click.echo(f"    Variant A: temp={baseline_temp:.2f}, top_p={baseline_top_p:.2f} (baseline)")
            click.echo(f"    Variant B: temp={baseline_temp + 0.1:.2f}, top_p={baseline_top_p + 0.1:.2f} (creative/exploratory)")
            click.echo(f"    Variant C: temp={baseline_temp - 0.1:.2f}, top_p={baseline_top_p - 0.1:.2f} (focused/deterministic)")
            
            variant_paths = generate_variants(current_file, {"rounds": iteration_history} if iteration_history else {})
            
            # Show variant content for debugging
            click.echo("Generated variants:")
            for name, path in variant_paths.items():
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                click.echo(f"  {name} ({len(content)} chars): {content[:100]}...")
            
            # Run objective evaluation on each variant
            click.echo("Running objective evaluation...")
            objective_scores = {}
            
            for name, path in variant_paths.items():
                click.echo(f"  Evaluating variant {name}...")
                # Simplified evaluation - in real implementation this would use the full evaluation system
                scores = {"overall": len(content) - (1 if name != 'A' else 0)}
                objective_scores[name] = scores
                click.echo(f"    {name}: {scores.get('overall', 0):.1f}")
            
            # Select winner
            if auto_select:
                winner = _select_winner_automatically(objective_scores)
                click.echo(f"🤖 Auto-selected winner: {winner}")
            else:
                winner = _prompt_for_winner(objective_scores, round_num, rounds)
            
            # Record this round with baseline parameters
            round_record = {
                "round": round_num,
                "winner": winner,
                "objective_scores": objective_scores,
                "variant_paths": variant_paths,
                "baseline_params": {
                    "temp": baseline_temp,
                    "top_p": baseline_top_p
                }
            }
            iteration_history.append(round_record)
            
            # If this is the last round, apply the winner
            if round_num == rounds:
                click.echo(f"\n🏆 FINAL ROUND COMPLETE")
                click.echo(f"Applying winner {winner} to {target_path}...")
                _apply_winner(variant_paths[winner], target_path)
                _cleanup_variants(variant_paths)
                break
            else:
                # Use winner as base for next round
                click.echo(f"Using winner {winner} as base for next round...")
                # Copy winner to a temporary file for next round
                temp_file = os.path.join(CACHE, f"round_{round_num}_winner.ts")
                _apply_winner(variant_paths[winner], temp_file)
                current_file = temp_file
                _cleanup_variants(variant_paths)
        
        # Clean up any remaining temporary files
        for round_num in range(1, rounds):
            temp_file = os.path.join(CACHE, f"round_{round_num}_winner.ts")
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        # Save iteration history
        _save_iteration_history(target_path, iteration_history)
        
        # Print final summary
        _print_iteration_summary(target_path, iteration_history)
        
    except Exception as e:
        click.echo(f"Error during ABC iteration: {e}")
        raise SystemExit(1)

@cli.command("iter:finish")
@click.argument("target_path")
@click.option("--winner", required=True, type=click.Choice(['A', 'B', 'C']), help="Winner variant")
@click.option("--scores-file", help="Path to Cursor evaluation JSON")
def iter_finish(target_path, winner, scores_file):
    """Complete ABC iteration by selecting winner (legacy command)."""
    click.echo("⚠️  This command is deprecated. Use 'iter:cursor' for iterative ABC evaluation.")
    click.echo("The new system automatically handles multiple rounds and cleanup.")
    
    try:
        # Load winner variant
        winner_path = os.path.join(CACHE, f"variant_{winner}.ts")
        if not os.path.exists(winner_path):
            click.echo(f"Error: Winner variant {winner} not found. Run iter:cursor first.")
            raise SystemExit(1)
        
        with open(winner_path, 'r', encoding='utf-8') as f:
            winner_content = f.read()
        
        # Write winner to target path
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(winner_content)
        
        click.echo(f"Winner variant {winner} written to {target_path}")
        
        # Clean up variant files
        for variant in ['A', 'B', 'C']:
            variant_path = os.path.join(CACHE, f"variant_{variant}.ts")
            if os.path.exists(variant_path):
                os.remove(variant_path)
        
        click.echo("✅ Cleanup complete")
        
    except Exception as e:
        click.echo(f"❌ Error finishing iteration: {e}")
        raise SystemExit(1)
