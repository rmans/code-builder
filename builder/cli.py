#!/usr/bin/env python3
import os, json, datetime, glob, re, fnmatch, subprocess
import click
from jinja2 import Template
from pathlib import Path as PPath
from typing import Dict

ROOT  = os.path.dirname(os.path.dirname(__file__))
DOCS  = os.path.join(ROOT, "docs")
ADRS  = os.path.join(DOCS, "adrs")
TEMPL = os.path.join(DOCS, "templates")
CACHE = os.path.join(ROOT, "builder", "cache")

def _today(): return datetime.date.today().isoformat()

def _render(path, ctx):
    with open(path, "r", encoding="utf-8") as f:
        return Template(f.read()).render(**ctx)

@click.group()
def cli():
    """Code Builder CLI"""

# -------------------- ADR --------------------
@cli.command("adr:new")
@click.option("--title", required=True)
@click.option("--parent", default="ADR-0000")
@click.option("--related", multiple=True)
@click.option("--tags", default="")
def adr_new(title, parent, related, tags):
    os.makedirs(ADRS, exist_ok=True)
    existing = [p for p in glob.glob(os.path.join(ADRS, "ADR-*.md")) if "MASTER" not in p]
    if existing:
        last = sorted([int(p.split("ADR-")[-1].split(".md")[0]) for p in existing])[-1]
        next_id = f"ADR-{last+1:04d}"
    else:
        next_id = "ADR-0001"
    ctx = {
        "id": next_id, "title": title, "date": _today(), "parent": parent,
        "related_files": list(related), "tags": tags,
        "context": "", "decision": "", "consequences": "", "alternatives": ""
    }
    out = _render(os.path.join(TEMPL, "sub_adr.md.hbs"), ctx)
    out_path = os.path.join(ADRS, f"{next_id}.md")
    with open(out_path, "w", encoding="utf-8") as f: f.write(out)
    master = os.path.join(ADRS, "0000_MASTER_ADR.md")
    row = f"| {next_id} | {title} | proposed |  | ./{next_id}.md |\n"
    with open(master, "a", encoding="utf-8") as f: f.write(row)
    click.echo(f"Created {out_path}")

# -------------------- RULES LOADER --------------------
def _load_rules(feature, stacks):
    from rules_loader import load_rules
    return load_rules(feature or None, [s.strip() for s in stacks.split(",") if s.strip()])

# -------------------- PLAN --------------------
@cli.command("plan:sync")
@click.option("--feature", default="")
@click.option("--stacks", default="typescript,react")
def plan_sync(feature, stacks):
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
    """Infer feature from builder/feature_map.json for PATH."""
    fmap = {}
    try:
        fmap = json.loads(PPath("builder/feature_map.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    feature = ""
    for pattern, val in (fmap or {}).items():
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatchcase(path, pattern):
            feature = val
            break
    os.makedirs(CACHE, exist_ok=True)
    rules = _load_rules(feature, stacks)
    ctx = {
        "trace": {"prd":"PRD#TBD","arch":"ARCH#TBD","ux":"UX#TBD","integration":"INT#TBD","adrs":[]},
        "acceptance": ["compiles","tests pass"],
        "goal": "Scaffolded by plan:auto",
        "name": "Scaffold",
        "feature": feature,
        "rules": rules
    }
    with open(os.path.join(CACHE,"context.json"),"w",encoding="utf-8") as f:
        json.dump(ctx, f, indent=2)
    click.echo(f"plan:auto → feature='{feature or 'none'}' -> wrote builder/cache/context.json")

# -------------------- ABC ITERATION --------------------
def _abc_params(base_t=0.6, base_p=0.9, round_idx=0, variant="A"):
    adj = 0.0 if variant=="A" else (0.1 if variant=="B" else -0.1)
    scale = max(0.05, 0.1 - round_idx*0.015)
    return round(base_t*(1+adj*scale/0.1),2), round(base_p*(1+adj*scale/0.1),2)

@cli.command("iter:run")
@click.argument("target_path")
@click.option("--rounds", default=3)
def iter_run(target_path, rounds):
    os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
    history = []
    base_t, base_p = 0.6, 0.9
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
    with open(target_path, "w", encoding="utf-8") as f: f.write(best["content"])
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, "iter_history.json"), "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    click.echo(f"Finalized {target_path} with ABC loop ({rounds} rounds)")

# -------------------- RULES --------------------
@cli.command("rules:show")
@click.option("--feature", default="")
@click.option("--stacks", default="typescript,react")
def rules_show(feature, stacks):
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

# -------------------- EVALUATION --------------------
@cli.command("eval:objective")
@click.argument("path")
@click.option("--server", is_flag=True, help="Start server and create evaluation")
def eval_objective(path, server):
    """Run objective evaluation on an artifact"""
    if server:
        # Start server mode
        import sys
        sys.path.append(os.path.join(ROOT, "builder", "scripts"))
        from cursor_server import create_evaluation, start_server
        
        click.echo("🚀 Starting Cursor Bridge Server...")
        click.echo("📝 Creating evaluation...")
        
        eval_id = create_evaluation(path, "single")
        
        click.echo(f"✅ Evaluation created: {eval_id}")
        click.echo(f"🔗 Prompt URL: http://127.0.0.1:5000/prompt/{eval_id}")
        click.echo(f"📋 Copy this URL to Cursor Chat or Composer")
        click.echo(f"⏳ Waiting for Cursor response...")
        
        # Start server in background thread
        import threading
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait for completion with timeout
        import time
        import requests
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
                            
            except requests.exceptions.RequestException as e:
                click.echo(f"⚠️  Server check failed: {e}")
            except Exception as e:
                click.echo(f"⚠️  Error checking completion: {e}")
            
            time.sleep(2)  # Check every 2 seconds
        
        click.echo(f"⏰ Timeout reached ({max_wait_time}s). Evaluation may still be in progress.")
        click.echo(f"🔗 You can check status at: http://127.0.0.1:5000/")
        click.echo(f"📝 Evaluation ID: {eval_id}")
        return
    
    # Regular mode (existing logic)
    try:
        # Import evaluators
        import sys
        sys.path.append(os.path.join(ROOT, "builder", "evaluators"))
        from objective import evaluate_code, evaluate_doc
        from artifact_detector import detect_artifact_type
        
        # Detect artifact type
        artifact_type = detect_artifact_type(path)
        click.echo(f"Detected artifact type: {artifact_type}")
        
        # Run reports:all to generate JSON reports
        click.echo("Running reports:all...")
        result = subprocess.run(
            ["pnpm", "run", "reports:all"], 
            cwd=ROOT, 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            click.echo(f"Warning: reports:all failed: {result.stderr}")
        
        # Run objective evaluation
        if artifact_type == 'code':
            scores = evaluate_code(path)
        else:
            scores = evaluate_doc(path, artifact_type)
        
        # Print scores
        click.echo("Objective Scores:")
        click.echo(json.dumps(scores, indent=2))
        
        # Save to cache
        os.makedirs(CACHE, exist_ok=True)
        output_path = os.path.join(CACHE, "last_objective.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "artifact_path": path,
                "artifact_type": artifact_type,
                "scores": scores,
                "timestamp": datetime.datetime.now().isoformat()
            }, f, indent=2)
        
        click.echo(f"Saved to {output_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

@cli.command("eval:prepare")
@click.argument("path")
@click.option("--server", is_flag=True, help="Start server and create evaluation")
def eval_prepare(path, server):
    """Prepare evaluation prompt for Cursor"""
    if server:
        # Use server mode (same as eval:objective --server)
        eval_objective(path, True)
        return
    
    # Regular mode (existing logic)
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
        
        # Import prompt builder
        import sys
        sys.path.append(os.path.join(ROOT, "builder", "prompts"))
        sys.path.append(os.path.join(ROOT, "builder", "evaluators"))
        from evaluation_prompt import build_single_eval_prompt
        from artifact_detector import detect_artifact_type
        
        # Generate prompt
        artifact_type = detect_artifact_type(path)
        prompt = build_single_eval_prompt(path, artifact_type)
        
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
    """Complete evaluation by blending objective and subjective scores"""
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
        config_path = os.path.join(ROOT, "docs", "eval", "config.yaml")
        import yaml
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except Exception:
            config = {}
        
        artifact_type = objective_data.get("artifact_type", "code")
        artifact_weights = config.get("artifact_weights", {}).get(artifact_type, {"objective": 0.7, "subjective": 0.3})
        
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
        final_eval = {
            "artifact_path": path,
            "artifact_type": artifact_type,
            "objective_scores": objective_scores,
            "subjective_scores": subjective_scores,
            "blended_scores": blended_scores,
            "overall_score": overall_blended,
            "weights": artifact_weights,
            "cursor_reasoning": cursor_data.get("reasoning", ""),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Save final evaluation
        os.makedirs(CACHE, exist_ok=True)
        final_path = os.path.join(CACHE, "final_eval.json")
        with open(final_path, "w", encoding="utf-8") as f:
            json.dump(final_eval, f, indent=2)
        
        # Print results
        click.echo("Final Evaluation Results:")
        click.echo(f"Overall Score: {overall_blended:.1f}")
        click.echo(f"Objective: {objective_scores.get('overall', 0):.1f} (weight: {artifact_weights['objective']})")
        click.echo(f"Subjective: {cursor_data.get('overall_score', 0):.1f} (weight: {artifact_weights['subjective']})")
        click.echo(f"Saved to {final_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

# -------------------- ABC ITERATION --------------------
def generate_variants(target_path: str) -> Dict[str, str]:
    """Generate A/B/C variants of a file (simple generator)"""
    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Simple variant generation - add comments/annotations
        variants = {
            "A": original_content,  # Original
            "B": f"// Variant B: Enhanced version\n{original_content}",
            "C": f"// Variant C: Alternative approach\n{original_content.replace('export const', 'export function')}"
        }
        
        # Save variants to cache
        os.makedirs(CACHE, exist_ok=True)
        variant_paths = {}
        for name, content in variants.items():
            variant_path = os.path.join(CACHE, f"variant_{name}.ts")
            with open(variant_path, 'w', encoding='utf-8') as f:
                f.write(content)
            variant_paths[name] = variant_path
        
        return variant_paths
    except Exception as e:
        click.echo(f"Error generating variants: {e}")
        raise SystemExit(1)

@cli.command("iter:cursor")
@click.argument("target_path")
@click.option("--rounds", default=1, help="Number of ABC rounds")
def iter_cursor(target_path, rounds):
    """Run ABC iteration with Cursor evaluation"""
    try:
        # Generate variants
        click.echo("Generating A/B/C variants...")
        variant_paths = generate_variants(target_path)
        
        # Run objective evaluation on each variant
        click.echo("Running objective evaluation on variants...")
        import sys
        sys.path.append(os.path.join(ROOT, "builder", "evaluators"))
        from objective import evaluate_code, evaluate_doc
        from artifact_detector import detect_artifact_type
        
        artifact_type = detect_artifact_type(target_path)
        objective_scores = {}
        
        for name, path in variant_paths.items():
            click.echo(f"Evaluating variant {name}...")
            if artifact_type == 'code':
                scores = evaluate_code(path)
            else:
                scores = evaluate_doc(path, artifact_type)
            objective_scores[name] = scores
        
        # Build ABC comparison prompt
        click.echo("Building ABC comparison prompt...")
        sys.path.append(os.path.join(ROOT, "builder", "prompts"))
        from evaluation_prompt import build_abc_eval_prompt
        
        prompt = build_abc_eval_prompt(variant_paths, objective_scores)
        
        # Save prompt
        prompt_path = os.path.join(CACHE, "abc_prompt.md")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        # Print instructions
        click.echo("\n" + "="*60)
        click.echo("ABC ITERATION READY")
        click.echo("="*60)
        click.echo(f"1. Copy {prompt_path} to Cursor")
        click.echo("2. Get Cursor's evaluation (JSON format)")
        click.echo("3. Run: python builder/cli.py iter:finish {target_path} --winner A|B|C --scores-file <cursor_response.json>")
        click.echo("\nObjective Scores:")
        for name, scores in objective_scores.items():
            click.echo(f"  {name}: {scores.get('overall', 0):.1f}")
        click.echo("="*60)
        
    except Exception as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

@cli.command("iter:finish")
@click.argument("target_path")
@click.option("--winner", required=True, type=click.Choice(['A', 'B', 'C']), help="Winner variant")
@click.option("--scores-file", help="Path to Cursor evaluation JSON")
def iter_finish(target_path, winner, scores_file):
    """Complete ABC iteration by selecting winner"""
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
        
        # Load objective scores for all variants
        objective_scores = {}
        for variant in ['A', 'B', 'C']:
            variant_path = os.path.join(CACHE, f"variant_{variant}.ts")
            if os.path.exists(variant_path):
                # Re-run evaluation to get fresh scores
                import sys
                sys.path.append(os.path.join(ROOT, "builder", "evaluators"))
                from objective import evaluate_code, evaluate_doc
                from artifact_detector import detect_artifact_type
                
                artifact_type = detect_artifact_type(target_path)
                if artifact_type == 'code':
                    scores = evaluate_code(variant_path)
                else:
                    scores = evaluate_doc(variant_path, artifact_type)
                objective_scores[variant] = scores
        
        # Load Cursor evaluation if provided
        cursor_evaluation = None
        if scores_file and os.path.exists(scores_file):
            with open(scores_file, 'r', encoding='utf-8') as f:
                cursor_evaluation = json.load(f)
        
        # Create iteration record
        iteration_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "target_path": target_path,
            "winner": winner,
            "objective_scores": objective_scores,
            "cursor_evaluation": cursor_evaluation,
            "round": 1  # Could be enhanced to track multiple rounds
        }
        
        # Append to iteration history
        history_path = os.path.join(CACHE, "iter_history.json")
        history = []
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append(iteration_record)
        
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
        
        # Print summary
        click.echo("\n" + "="*60)
        click.echo("ABC ITERATION COMPLETE")
        click.echo("="*60)
        click.echo(f"Winner: {winner}")
        click.echo(f"Target: {target_path}")
        click.echo(f"History: {history_path}")
        
        click.echo("\nObjective Scores Summary:")
        for variant, scores in objective_scores.items():
            marker = " ← WINNER" if variant == winner else ""
            click.echo(f"  {variant}: {scores.get('overall', 0):.1f}{marker}")
        
        if cursor_evaluation:
            click.echo(f"\nCursor Evaluation: {cursor_evaluation.get('winner', 'N/A')}")
            click.echo(f"Confidence: {cursor_evaluation.get('confidence', 'N/A')}")
        
        click.echo("="*60)
        
    except Exception as e:
        click.echo(f"Error: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    cli()
