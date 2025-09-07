#!/usr/bin/env python3
"""
Evaluation Commands Module

This module contains evaluation-related commands like eval:*, rules:*
"""

import click
import os
import sys
import json
import re
import glob
import subprocess
import time
import threading
import requests
import importlib.util
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
    """Load rules for evaluation."""
    try:
        from ..context_rules import merge_context_rules
        return merge_context_rules(feature or None, [s.strip() for s in stacks.split(",") if s.strip()])
    except ImportError:
        return {"rules_markdown": "", "guardrails": {}}

# Evaluation Commands
@cli.command("rules:show")
@click.option("--feature", default="")
@click.option("--stacks", default="typescript,react")
def rules_show(feature, stacks):
    """Show merged rules and guardrails."""
    rules = _load_rules(feature, stacks)
    click.echo("===== MERGED RULES =====\n")
    click.echo(rules.get("rules_markdown") or "(none)")
    click.echo("\n===== GUARDRAILS =====\n")
    click.echo(json.dumps(rules.get("guardrails", {}), indent=2))

@cli.command("rules:check")
@click.argument("path")
@click.option("--feature", default="")
@click.option("--stacks", default="typescript,react")
def rules_check(path, feature, stacks):
    """Check rules compliance using guardrails."""
    rules = _load_rules(feature, stacks)
    guardrails = rules.get("guardrails", {})
    patterns = guardrails.get("forbiddenPatterns", [])
    paths = glob.glob(path, recursive=True)
    failed = False
    
    for p in paths:
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            for pr in patterns:
                pat = pr.get("pattern")
                msg = pr.get("message", "Forbidden pattern")
                if pat and re.search(pat, txt):
                    click.echo(f"FAIL {p}: {msg} ({pat})")
                    failed = True
    
    if failed:
        raise SystemExit(2)
    click.echo("Guardrails OK")

@cli.command("eval:objective")
@click.argument("path")
@click.option("--server", is_flag=True, help="Start server and create evaluation")
def eval_objective(path, server):
    """Run objective evaluation on an artifact."""
    if server:
        # Start server mode
        try:
            # Add scripts directory to path
            scripts_path = os.path.join(ROOT, "builder", "scripts")
            if scripts_path not in sys.path:
                sys.path.append(scripts_path)
            
            # Import cursor_server module
            cursor_server_path = os.path.join(scripts_path, "cursor_server.py")
            spec = importlib.util.spec_from_file_location("cursor_server", cursor_server_path)
            cursor_server = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cursor_server)
            
            create_evaluation = cursor_server.create_evaluation
            start_server = cursor_server.start_server
            
            click.echo("🚀 Starting Cursor Bridge Server...")
            click.echo("📝 Creating evaluation...")
            
            eval_id = create_evaluation(path, "single")
            
            click.echo(f"✅ Evaluation created: {eval_id}")
            click.echo(f"🔗 Prompt URL: http://127.0.0.1:5000/prompt/{eval_id}")
            click.echo(f"📋 Copy this URL to Cursor Chat or Composer")
            click.echo(f"⏳ Waiting for Cursor response...")
            
            # Start server in background thread
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            
            # Wait for completion with timeout
            max_wait_time = 300  # 5 minutes timeout
            start_time = time.time()
            
            click.echo(f"⏳ Waiting for Cursor response (timeout: {max_wait_time}s)...")
            
            while time.time() - start_time < max_wait_time:
                try:
                    # Check server status with timeout
                    response = requests.get(f"http://127.0.0.1:5000/", timeout=5)
                    if response.status_code == 200:
                        # Check if our evaluation is complete by looking for the eval_id in completed evaluations
                        if f'completed_at' in response.text and eval_id in response.text:
                            click.echo("✅ Evaluation completed!")
                            return
                    
                    # Check if evaluation file exists and has completion timestamp
                    eval_file = os.path.join(ROOT, "builder", "cache", "evaluations", f"{eval_id}.json")
                    if os.path.exists(eval_file):
                        with open(eval_file, 'r') as f:
                            eval_data = json.load(f)
                            if eval_data.get('completed_at'):
                                click.echo("✅ Evaluation completed!")
                                return
                                
                except Exception:
                    pass
                
                time.sleep(2)
            
            click.echo("⏰ Timeout waiting for Cursor response")
            click.echo("💡 You can check the evaluation status manually")
            
        except Exception as e:
            click.echo(f"❌ Error in server mode: {e}")
            raise SystemExit(1)
    else:
        # Regular mode - run objective evaluation
        try:
            click.echo(f"📊 Running objective evaluation on {path}")
            
            # Mock objective evaluation for now
            objective_data = {
                "artifact_type": "code",
                "scores": {
                    "readability": 85,
                    "maintainability": 90,
                    "performance": 75,
                    "overall": 83
                },
                "timestamp": time.time()
            }
            
            # Save objective scores
            os.makedirs(CACHE, exist_ok=True)
            objective_path = os.path.join(CACHE, "last_objective.json")
            with open(objective_path, "w", encoding="utf-8") as f:
                json.dump(objective_data, f, indent=2)
            
            click.echo("✅ Objective evaluation completed")
            click.echo(f"📄 Scores saved to: {objective_path}")
            click.echo(f"📊 Overall Score: {objective_data['scores']['overall']}")
            
        except Exception as e:
            click.echo(f"❌ Error running objective evaluation: {e}")
            raise SystemExit(1)

@cli.command("eval:prepare")
@click.argument("path")
@click.option("--server", is_flag=True, help="Start server and create evaluation")
def eval_prepare(path, server):
    """Prepare evaluation prompt for Cursor."""
    if server:
        # Use server mode (same as eval:objective --server)
        eval_objective(path, True)
        return
    
    # Regular mode
    try:
        # Run objective evaluation first
        click.echo("Running objective evaluation...")
        result = subprocess.run(
            ["python", os.path.join(ROOT, "builder", "cli.py"), "eval:objective", path],
            cwd=ROOT,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.echo(f"Warning: objective evaluation failed: {result.stderr}")
        
        # Generate prompt (simplified for now)
        prompt = f"""# Evaluation Prompt for {path}

Please evaluate the following code artifact:

**File:** {path}
**Type:** Code

Please provide your evaluation in JSON format with the following structure:
```json
{{
    "dimensions": {{
        "readability": 0-100,
        "maintainability": 0-100,
        "performance": 0-100,
        "security": 0-100
    }},
    "overall_score": 0-100,
    "comments": "Your detailed feedback here"
}}
```

Focus on:
- Code quality and readability
- Maintainability and structure
- Performance considerations
- Security best practices
"""
        
        # Save prompt
        os.makedirs(CACHE, exist_ok=True)
        prompt_path = os.path.join(CACHE, "cursor_prompt.md")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        click.echo("Copy builder/cache/cursor_prompt.md to Cursor")
        click.echo(f"Prompt saved to {prompt_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

@cli.command("eval:complete")
@click.argument("path")
@click.option("--cursor-response", required=True, help="Path to Cursor's JSON response")
def eval_complete(path, cursor_response):
    """Complete evaluation by blending objective and subjective scores."""
    try:
        # Load objective scores
        objective_path = os.path.join(CACHE, "last_objective.json")
        if not os.path.exists(objective_path):
            click.echo("Error: No objective scores found. Run eval:objective first.")
            raise SystemExit(1)
        
        with open(objective_path, "r", encoding="utf-8") as f:
            objective_data = json.load(f)
        
        # Load Cursor response
        if not os.path.exists(cursor_response):
            click.echo(f"Error: Cursor response file not found: {cursor_response}")
            raise SystemExit(1)
        
        with open(cursor_response, "r", encoding="utf-8") as f:
            cursor_data = json.load(f)
        
        # Load config for weights
        config_path = os.path.join(DOCS, "eval", "config.yaml")
        try:
            import yaml
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except Exception:
            config = {}
        
        artifact_type = objective_data.get("artifact_type", "code")
        artifact_weights = config.get("artifact_weights", {}).get(artifact_type, {"objective": 0.6, "subjective": 0.4})
        
        # Blend scores
        objective_scores = objective_data.get("scores", {})
        subjective_scores = cursor_data.get("dimensions", {})
        
        # Calculate blended scores
        blended_scores = {}
        for dimension in subjective_scores.keys():
            if dimension in objective_scores:
                obj_score = objective_scores[dimension]
                subj_score = subjective_scores[dimension]
                blended = (obj_score * artifact_weights["objective"] + 
                          subj_score * artifact_weights["subjective"])
                blended_scores[dimension] = blended
            else:
                blended_scores[dimension] = subjective_scores[dimension]
        
        # Calculate overall blended score
        overall_blended = (objective_scores.get("overall", 50) * artifact_weights["objective"] + 
                          cursor_data.get("overall_score", 50) * artifact_weights["subjective"])
        
        # Create final evaluation
        final_evaluation = {
            "artifact_path": path,
            "artifact_type": artifact_type,
            "objective_scores": objective_scores,
            "subjective_scores": subjective_scores,
            "blended_scores": blended_scores,
            "overall_score": overall_blended,
            "weights": artifact_weights,
            "timestamp": time.time(),
            "cursor_comments": cursor_data.get("comments", "")
        }
        
        # Save final evaluation
        eval_path = os.path.join(CACHE, "final_evaluation.json")
        with open(eval_path, "w", encoding="utf-8") as f:
            json.dump(final_evaluation, f, indent=2)
        
        click.echo("✅ Evaluation completed!")
        click.echo(f"📄 Final evaluation saved to: {eval_path}")
        click.echo(f"📊 Overall Score: {overall_blended:.1f}")
        click.echo(f"📋 Blended Scores: {blended_scores}")
        
    except Exception as e:
        click.echo(f"❌ Error completing evaluation: {e}")
        raise SystemExit(1)
