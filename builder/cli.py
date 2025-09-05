#!/usr/bin/env python3
import os, json, datetime, glob, re, fnmatch, subprocess
import click
from jinja2 import Template
from pathlib import Path as PPath
from typing import Dict
import requests

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
    from context_rules import merge_context_rules
    return merge_context_rules(feature or None, [s.strip() for s in stacks.split(",") if s.strip()])

# -------------------- DOCUMENT HELPERS --------------------
import re, yaml
from pathlib import Path

def _doc_load_front_matter(path):
    txt = Path(path).read_text(encoding="utf-8")
    m = re.search(r'^---\n(.*?)\n---\n', txt, flags=re.S)
    if not m:
        return None, txt, None
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        fm = {}
    return fm, txt, m

def _doc_save_front_matter(path, front, txt, m):
    new = '---\n' + yaml.safe_dump(front, sort_keys=False).strip() + '\n---\n' + txt[m.end():]
    Path(path).write_text(new, encoding="utf-8")

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
    """Infer feature from builder/feature_map.json for PATH and build context."""
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
    
    click.echo(f"🔍 Detected feature: '{feature or 'none'}' for path: {path}")
    
    # Call ctx:build after feature detection
    try:
        click.echo("🔧 Building context package...")
        
        # Import ctx_build function logic
        import yaml
        import re
        from pathlib import Path
        
        # Ensure cache directory exists
        os.makedirs(CACHE, exist_ok=True)
        
        # Load rules
        rules = _load_rules(feature, stacks)
        
        # Find nearest PRD
        prd_content = ""
        prd_metadata = {}
        adr_contents = []
        
        # Look for PRD in same directory or parent directories
        target_dir = os.path.dirname(path)
        prd_found = False
        
        # Search for PRD files
        for root, dirs, files in os.walk(DOCS):
            for file in files:
                if file.endswith('.md') and 'prd' in file.lower():
                    prd_path = os.path.join(root, file)
                    try:
                        with open(prd_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Try to parse front-matter for metadata
                            metadata = {}
                            try:
                                with open(prd_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    if content.startswith('---'):
                                        parts = content.split('---', 2)
                                        if len(parts) >= 3:
                                            front_matter = parts[1]
                                            metadata = yaml.safe_load(front_matter) or {}
                                            prd_content = parts[2]
                                    else:
                                        prd_content = content
                                
                                prd_metadata = {
                                    'type': metadata.get('type', 'prd'),
                                    'id': metadata.get('id', file.replace('.md', '')),
                                    'title': metadata.get('title', file.replace('.md', '')),
                                    'status': metadata.get('status', 'draft'),
                                    'owner': metadata.get('owner', 'TBD'),
                                    'created': metadata.get('created', _today()),
                                    'links': metadata.get('links', [])
                                }
                                prd_found = True
                                break
                            except Exception:
                                pass
                    except Exception:
                        pass
            if prd_found:
                break
        
        # Find ADRs
        for root, dirs, files in os.walk(ADRS):
            for file in files:
                if file.endswith('.md') and file.startswith('ADR-'):
                    adr_path = os.path.join(root, file)
                    try:
                        with open(adr_path, 'r', encoding='utf-8') as f:
                            adr_contents.append(f.read())
                    except Exception:
                        pass
        
        # Get code excerpts
        code_excerpts = []
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    excerpt = '\n'.join(lines[:30])
                    if len(lines) > 30:
                        excerpt += '\n... (truncated)'
                    code_excerpts.append({
                        'path': path,
                        'excerpt': excerpt,
                        'line_count': len(lines)
                    })
            except Exception:
                pass
        
        # Get test excerpts
        test_excerpts = []
        test_path = path.replace('.ts', '.test.ts').replace('.js', '.test.js')
        if os.path.exists(test_path):
            try:
                with open(test_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    excerpt = '\n'.join(lines[:30])
                    if len(lines) > 30:
                        excerpt += '\n... (truncated)'
                    test_excerpts.append({
                        'path': test_path,
                        'excerpt': excerpt,
                        'line_count': len(lines)
                    })
            except Exception:
                pass
        
        # Extract acceptance criteria from PRD
        acceptance_criteria = []
        if prd_content:
            # Look for acceptance criteria section
            lines = prd_content.split('\n')
            in_acceptance = False
            for line in lines:
                if 'acceptance criteria' in line.lower() or 'acceptance' in line.lower():
                    in_acceptance = True
                    continue
                if in_acceptance and line.strip().startswith('#'):
                    break
                if in_acceptance and line.strip().startswith('-'):
                    acceptance_criteria.append(line.strip())
        
        # Build context package
        context_package = {
            'target_path': path,
            'purpose': 'implement',
            'feature': feature,
            'stacks': stacks.split(',') if stacks else [],
            'rules': rules,
            'prd': {
                'content': prd_content,
                'metadata': prd_metadata
            },
            'adrs': adr_contents,
            'code_excerpts': code_excerpts,
            'test_excerpts': test_excerpts,
            'acceptance_criteria': acceptance_criteria,
            'generated_at': _today()
        }
        
        # Ensure all values are JSON serializable
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif hasattr(obj, 'isoformat'):  # datetime objects
                return obj.isoformat()
            else:
                return obj
        
        context_package = make_serializable(context_package)
        
        # Write pack_context.json
        pack_context_path = os.path.join(CACHE, "pack_context.json")
        try:
            with open(pack_context_path, "w", encoding="utf-8") as f:
                json.dump(context_package, f, indent=2, ensure_ascii=False)
            click.echo(f"✅ Created {pack_context_path}")
        except Exception as e:
            click.echo(f"Error writing pack_context.json: {e}")
            raise SystemExit(1)
        
        # Generate summary
        click.echo(f"\n📊 Context Summary:")
        click.echo(f"  Target: {path}")
        click.echo(f"  Feature: {feature or 'none'}")
        click.echo(f"  Purpose: implement")
        click.echo(f"  Stacks: {', '.join(stacks.split(','))}")
        click.echo(f"  PRD: {'Found' if prd_content else 'Not found'}")
        click.echo(f"  ADRs: {len(adr_contents)}")
        click.echo(f"  Code files: {len(code_excerpts)}")
        click.echo(f"  Test files: {len(test_excerpts)}")
        click.echo(f"  Acceptance criteria: {len(acceptance_criteria)}")
        
        # Legacy context.json for backward compatibility
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
        click.echo(f"✅ Also wrote builder/cache/context.json")
        
    except Exception as e:
        click.echo(f"❌ Error building context: {e}")
        # Fallback to original behavior
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
        click.echo(f"⚠️  Fallback: wrote builder/cache/context.json only")

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
        import importlib.util
        
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
        import threading
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Wait for completion with timeout
        import time
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
        sys.path.append(os.path.join(ROOT, "builder"))
        from evaluators.objective import evaluate_code, evaluate_doc
        from evaluators.artifact_detector import detect_artifact_type
        
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
        sys.path.append(os.path.join(ROOT, "builder"))
        from prompts.evaluation_prompt import build_single_eval_prompt
        from evaluators.artifact_detector import detect_artifact_type
        
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
        sys.path.append(os.path.join(ROOT, "builder"))
        from evaluators.objective import evaluate_code, evaluate_doc
        from evaluators.artifact_detector import detect_artifact_type
        
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
        from prompts.evaluation_prompt import build_abc_eval_prompt
        
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
                sys.path.append(os.path.join(ROOT, "builder"))
                from evaluators.objective import evaluate_code, evaluate_doc
                from evaluators.artifact_detector import detect_artifact_type
                
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

# -------------------- DOC FACTORY --------------------
@cli.command("doc:new")
@click.argument("dtype", type=click.Choice(['prd', 'arch', 'integrations', 'ux', 'impl', 'exec', 'tasks']))
@click.option("--title", required=True, help="Document title")
@click.option("--owner", default="", help="Document owner")
@click.option("--links", multiple=True, help="Links to other documents (format: type:id)")
def doc_new(dtype, title, owner, links):
    """Create a new document from template"""
    # Validate required title
    if not title or not title.strip():
        click.echo("Error: --title is required and cannot be empty")
        raise SystemExit(1)
    
    # Generate slug and ID
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    doc_id = f"{dtype.upper()}-{slug[:20]}"  # Limit slug length
    
    # Set default owner if not provided
    if not owner:
        owner = "TBD"
    
    # Parse links
    parsed_links = {}
    for link in links:
        if ':' in link:
            link_type, link_id = link.split(':', 1)
            if link_type not in parsed_links:
                parsed_links[link_type] = []
            parsed_links[link_type].append(link_id)
    
    # Create context for template rendering
    ctx = {
        "id": doc_id,
        "title": title,
        "owner": owner,
        "created": _today(),
        "links": parsed_links
    }
    
    # Determine output directory and file path
    doc_dir = os.path.join(DOCS, dtype)
    os.makedirs(doc_dir, exist_ok=True)
    
    # Load and render template
    template_path = os.path.join(TEMPL, f"{dtype}.md.hbs")
    if not os.path.exists(template_path):
        click.echo(f"Error: Template {template_path} not found")
        raise SystemExit(1)
    
    try:
        content = _render(template_path, ctx)
    except Exception as e:
        click.echo(f"Error rendering template: {e}")
        raise SystemExit(1)
    
    # Write the document
    output_path = os.path.join(doc_dir, f"{doc_id}.md")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        click.echo(f"Created {output_path}")
    except Exception as e:
        click.echo(f"Error writing file: {e}")
        raise SystemExit(1)

@cli.command("doc:index")
@click.option("--no-warn", is_flag=True, help="Disable warnings about missing link targets")
def doc_index(no_warn):
    """Generate documentation index in docs/README.md"""
    import yaml
    from collections import defaultdict
    
    # Document type configurations
    doc_types = {
        'prd': {'name': 'Product Requirements', 'icon': '📋', 'description': 'Product requirements and specifications'},
        'arch': {'name': 'Architecture', 'icon': '🏗️', 'description': 'Architectural decisions and designs'},
        'integrations': {'name': 'Integrations', 'icon': '🔗', 'description': 'Integration specifications and APIs'},
        'ux': {'name': 'User Experience', 'icon': '🎨', 'description': 'UX designs and user research'},
        'impl': {'name': 'Implementation', 'icon': '⚙️', 'description': 'Implementation details and technical specs'},
        'exec': {'name': 'Executive', 'icon': '📊', 'description': 'Executive summaries and business documents'},
        'tasks': {'name': 'Tasks', 'icon': '✅', 'description': 'Task definitions and work items'}
    }
    
    # Scan for documents
    documents = defaultdict(list)
    all_doc_ids = set()
    warnings = []
    
    for doc_type in doc_types.keys():
        doc_dir = os.path.join(DOCS, doc_type)
        if os.path.exists(doc_dir):
            for filename in os.listdir(doc_dir):
                if filename.endswith('.md') and not filename.startswith('.'):
                    filepath = os.path.join(doc_dir, filename)
                    doc_id = filename.replace('.md', '')
                    all_doc_ids.add(doc_id)
                    
                    # Try to parse front-matter for metadata
                    metadata = {}
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.startswith('---'):
                                parts = content.split('---', 2)
                                if len(parts) >= 3:
                                    yaml_content = parts[1].strip()
                                    metadata = yaml.safe_load(yaml_content) or {}
                    except Exception as e:
                        if not no_warn:
                            warnings.append(f"⚠️  Could not parse front-matter for {filepath}: {e}")
                    
                    # Ensure links is always a dict
                    links = metadata.get('links', {})
                    if isinstance(links, list):
                        # Convert list of dicts to single dict
                        parsed_links = {}
                        for link_item in links:
                            if isinstance(link_item, dict):
                                parsed_links.update(link_item)
                        links = parsed_links
                    
                    documents[doc_type].append({
                        'id': doc_id,
                        'filename': filename,
                        'path': filepath,
                        'title': metadata.get('title', doc_id),
                        'status': metadata.get('status', 'unknown'),
                        'owner': metadata.get('owner', 'TBD'),
                        'created': metadata.get('created', 'unknown'),
                        'links': links
                    })
    
    # Check for missing link targets
    if not no_warn:
        for doc_type, docs in documents.items():
            for doc in docs:
                links = doc['links']
                if isinstance(links, dict):
                    for link_type, link_ids in links.items():
                        if isinstance(link_ids, list):
                            for link_id in link_ids:
                                if link_id not in all_doc_ids:
                                    warnings.append(f"⚠️  {doc['id']} links to missing {link_type}:{link_id}")
    
    # Generate README content
    readme_content = """# Documentation Layer

This repo uses docs to drive codegen, decisions, and evaluation.

---

## Document Index

"""
    
    # Add document sections
    for doc_type, config in doc_types.items():
        docs = documents[doc_type]
        if docs:
            readme_content += f"### {config['icon']} {config['name']}\n"
            readme_content += f"*{config['description']}*\n\n"
            
            for doc in sorted(docs, key=lambda x: x['created'], reverse=True):
                status_emoji = {
                    'draft': '📝',
                    'review': '👀', 
                    'approved': '✅',
                    'archived': '📦',
                    'unknown': '❓'
                }.get(doc['status'], '❓')
                
                readme_content += f"- {status_emoji} **{doc['title']}** (`{doc['id']}`)\n"
                readme_content += f"  - Owner: {doc['owner']} | Created: {doc['created']}\n"
                
                # Show links if any
                has_links = any(links for links in doc['links'].values() if links)
                if has_links:
                    readme_content += "  - Links: "
                    link_parts = []
                    for link_type, link_ids in doc['links'].items():
                        if link_ids:
                            link_parts.append(f"{link_type}:{', '.join(link_ids)}")
                    readme_content += " | ".join(link_parts) + "\n"
                
                readme_content += "\n"
        else:
            readme_content += f"### {config['icon']} {config['name']}\n"
            readme_content += f"*{config['description']}*\n"
            readme_content += f"*No documents found*\n\n"
    
    # Add existing sections
    readme_content += """---

## ADRs (docs/adrs/)
- `0000_MASTER_ADR.md` = index of all decisions
- Sub ADRs like `ADR-0001.md` created by `builder:adr:new`
- Each ADR records context, decision, consequences, alternatives

---

## Templates (docs/templates/)
- Jinja2 templates for ADRs and specs
- Used by CLI to render files

---

## Rules (docs/rules/)
- `00-global.md`, `10-project.md` = global + project-wide rules
- `stack/` (e.g. typescript, react, http-client)
- `feature/` (auth, content-engine, etc.)
- `guardrails.json` = forbidden patterns + hints

---

## Evaluation (docs/eval/)
- `config.yaml` = evaluation weights and configuration
- Defines objective vs subjective weight distribution
- Configures tool paths and scoring weights

---

## Usage Guides
- `USAGE-Cursor-Evaluation.md` = Complete evaluation workflow guide
- `CURSOR-Custom-Commands.md` = Cursor integration setup

---

## Usage
- When editing a file, run `plan:auto <file>` → context.json merges rules + ADRs  
- Cursor/AI gets that context and generates compliant code
- Run `eval:objective <file>` → measure code quality objectively
- Use `--server` flag for interactive Cursor evaluation
- Use `doc:new <type> --title "Title"` → create new documents
- Use `doc:index` → update this index
"""
    
    # Write the README
    readme_path = os.path.join(DOCS, "README.md")
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        click.echo(f"✅ Updated {readme_path}")
    except Exception as e:
        click.echo(f"Error writing README: {e}")
        raise SystemExit(1)
    
    # Show warnings if any
    if warnings:
        click.echo("\n⚠️  Warnings:")
        for warning in warnings:
            click.echo(f"  {warning}")
        click.echo(f"\nTotal warnings: {len(warnings)}")
    else:
        click.echo("✅ No warnings found")

# -------------------- CONTEXT BUILDER --------------------
@cli.command("ctx:build")
@click.argument("target_path")
@click.option("--purpose", required=True, help="Purpose: implement, review, test, etc.")
@click.option("--feature", default="", help="Feature name for rules")
@click.option("--stacks", default="typescript,react", help="Comma-separated stack names")
@click.option("--token-limit", default=8000, help="Token budget limit")
def ctx_build(target_path, purpose, feature, stacks, token_limit):
    """Build context package for a target path"""
    import yaml
    import re
    from pathlib import Path
    
    # Ensure cache directory exists
    os.makedirs(CACHE, exist_ok=True)
    
    # Load rules
    rules = _load_rules(feature, stacks)
    
    # Find nearest PRD
    prd_content = ""
    prd_metadata = {}
    adr_contents = []
    
    # Look for PRD in same directory or parent directories
    target_dir = os.path.dirname(target_path)
    prd_found = False
    
    # Search for PRD files
    for root, dirs, files in os.walk(DOCS):
        if root.startswith(os.path.join(DOCS, "prd")):
            for file in files:
                if file.endswith('.md'):
                    prd_path = os.path.join(root, file)
                    try:
                        with open(prd_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.startswith('---'):
                                parts = content.split('---', 2)
                                if len(parts) >= 3:
                                    yaml_content = parts[1].strip()
                                    metadata = yaml.safe_load(yaml_content) or {}
                                    if metadata.get('type') == 'prd':
                                        prd_content = content
                                        prd_metadata = metadata
                                        prd_found = True
                                        break
                    except Exception:
                        continue
        if prd_found:
            break
    
    # Extract ADR references from PRD
    if prd_content:
        # Look for ADR references in PRD content
        adr_refs = re.findall(r'ADR-\d+', prd_content)
        for adr_ref in adr_refs:
            adr_path = os.path.join(DOCS, "adrs", f"{adr_ref}.md")
            if os.path.exists(adr_path):
                try:
                    with open(adr_path, 'r', encoding='utf-8') as f:
                        adr_contents.append(f.read())
                except Exception:
                    continue
    
    # Extract code excerpts
    code_excerpts = []
    if os.path.exists(target_path):
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract first 50 lines as excerpt
                lines = content.split('\n')
                excerpt = '\n'.join(lines[:50])
                if len(lines) > 50:
                    excerpt += '\n... (truncated)'
                code_excerpts.append({
                    'path': target_path,
                    'excerpt': excerpt,
                    'line_count': len(lines)
                })
        except Exception:
            pass
    
    # Look for test files
    test_excerpts = []
    test_path = target_path.replace('.ts', '.test.ts').replace('.js', '.test.js')
    if os.path.exists(test_path):
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                excerpt = '\n'.join(lines[:30])
                if len(lines) > 30:
                    excerpt += '\n... (truncated)'
                test_excerpts.append({
                    'path': test_path,
                    'excerpt': excerpt,
                    'line_count': len(lines)
                })
        except Exception:
            pass
    
    # Extract acceptance criteria from PRD
    acceptance_criteria = []
    if prd_content:
        # Look for acceptance criteria section
        lines = prd_content.split('\n')
        in_acceptance = False
        for line in lines:
            if 'acceptance criteria' in line.lower() or 'acceptance' in line.lower():
                in_acceptance = True
                continue
            if in_acceptance and line.strip().startswith('#'):
                break
            if in_acceptance and line.strip().startswith('-'):
                acceptance_criteria.append(line.strip())
    
    # Build context package
    context_package = {
        'target_path': target_path,
        'purpose': purpose,
        'feature': feature,
        'stacks': stacks.split(',') if stacks else [],
        'rules': rules,
        'prd': {
            'content': prd_content,
            'metadata': prd_metadata
        },
        'adrs': adr_contents,
        'code_excerpts': code_excerpts,
        'test_excerpts': test_excerpts,
        'acceptance_criteria': acceptance_criteria,
        'generated_at': _today()
    }
    
    # Ensure all values are JSON serializable
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # datetime objects
            return obj.isoformat()
        else:
            return obj
    
    context_package = make_serializable(context_package)
    
    # Write pack_context.json
    pack_context_path = os.path.join(CACHE, "pack_context.json")
    try:
        with open(pack_context_path, "w", encoding="utf-8") as f:
            json.dump(context_package, f, indent=2, ensure_ascii=False)
        click.echo(f"✅ Created {pack_context_path}")
    except Exception as e:
        click.echo(f"Error writing pack_context.json: {e}")
        raise SystemExit(1)
    
    # Generate context.md
    context_md = f"""# Context Package

**Target**: `{target_path}`  
**Purpose**: {purpose}  
**Feature**: {feature or 'None'}  
**Stacks**: {', '.join(context_package['stacks'])}  
**Generated**: {_today()}

---

## Rules

{rules.get('rules_markdown', 'No rules found')}

---

## PRD

{prd_content if prd_content else 'No PRD found'}

---

## ADRs

{chr(10).join([f"### {i+1}\n\n{adr}" for i, adr in enumerate(adr_contents)]) if adr_contents else 'No ADRs found'}

---

## Code Excerpts

{chr(10).join([f"### {excerpt['path']}\n\n```\n{excerpt['excerpt']}\n```\n" for excerpt in code_excerpts]) if code_excerpts else 'No code excerpts found'}

---

## Test Excerpts

{chr(10).join([f"### {excerpt['path']}\n\n```\n{excerpt['excerpt']}\n```\n" for excerpt in test_excerpts]) if test_excerpts else 'No test excerpts found'}

---

## Acceptance Criteria

{chr(10).join([f"- {criteria}" for criteria in acceptance_criteria]) if acceptance_criteria else 'No acceptance criteria found'}
"""
    
    # Write context.md
    context_md_path = os.path.join(CACHE, "context.md")
    try:
        with open(context_md_path, "w", encoding="utf-8") as f:
            f.write(context_md)
        click.echo(f"✅ Created {context_md_path}")
    except Exception as e:
        click.echo(f"Error writing context.md: {e}")
        raise SystemExit(1)
    
    # Calculate token usage (rough estimate: 1 token ≈ 4 characters)
    def estimate_tokens(text):
        return len(text) // 4 if text else 0
    
    total_tokens = (
        estimate_tokens(rules.get('rules_markdown', '')) +
        estimate_tokens(prd_content) +
        sum(estimate_tokens(adr) for adr in adr_contents) +
        sum(estimate_tokens(excerpt['excerpt']) for excerpt in code_excerpts) +
        sum(estimate_tokens(excerpt['excerpt']) for excerpt in test_excerpts) +
        estimate_tokens('\n'.join(acceptance_criteria))
    )
    
    # Show summary
    click.echo(f"\n📦 Context Package Summary:")
    click.echo(f"  Rules: {len(rules.get('rules_markdown', '').split())} words")
    click.echo(f"  PRD: {'Found' if prd_content else 'Not found'}")
    click.echo(f"  ADRs: {len(adr_contents)}")
    click.echo(f"  Code excerpts: {len(code_excerpts)}")
    click.echo(f"  Test excerpts: {len(test_excerpts)}")
    click.echo(f"  Acceptance criteria: {len(acceptance_criteria)}")
    click.echo(f"  Estimated tokens: {total_tokens}/{token_limit}")
    
    if total_tokens > token_limit:
        click.echo(f"⚠️  Token budget exceeded! Consider reducing content or increasing --token-limit")
    elif total_tokens > token_limit * 0.8:
        click.echo(f"⚠️  Approaching token limit ({total_tokens}/{token_limit})")
    else:
        click.echo(f"✅ Token usage within budget")

# -------------------- CONTEXT BUILD HELPERS --------------------
def _build_enhanced_context_package(target_path, purpose, feature, stacks, token_limit, 
                                   selected_items, overflow_items, budget_summary, rules):
    """Build enhanced context package with all required fields"""
    
    # Group selected items by type
    items_by_type = {}
    for item in selected_items:
        item_type = item.type
        if item_type not in items_by_type:
            items_by_type[item_type] = []
        items_by_type[item_type].append(item)
    
    # Extract acceptance criteria from PRD items
    acceptance = []
    for item in items_by_type.get('acceptance', []):
        acceptance.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Extract decisions from ADR items
    decisions = []
    for item in items_by_type.get('adr', []):
        decisions.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Extract integrations
    integrations = []
    for item in items_by_type.get('integration', []):
        integrations.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Extract architecture items
    architecture = []
    for item in items_by_type.get('arch', []):
        architecture.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Extract UX items
    ux = []
    for item in items_by_type.get('ux', []):
        ux.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Extract code items
    code = []
    for item in items_by_type.get('code', []):
        code.append({
            'title': item.title,
            'content': item.content,
            'file_path': item.file_path,
            'source_anchor': item.source_anchor
        })
    
    # Build objective signals from existing reports
    objective_signals = _build_objective_signals()
    
    # Build provenance information
    provenance = _build_provenance(selected_items, overflow_items, budget_summary)
    
    # Build render information
    render = _build_render_info(target_path, purpose, feature, selected_items)
    
    return {
        'task': {
            'purpose': purpose,
            'target_path': target_path,
            'feature': feature
        },
        'constraints': {
            'rules_md': rules.get('rules_markdown', ''),
            'token_limit': token_limit,
            'budget_summary': budget_summary
        },
        'acceptance': acceptance,
        'decisions': decisions,
        'integrations': integrations,
        'architecture': architecture,
        'ux': ux,
        'code': code,
        'objective_signals': objective_signals,
        'provenance': provenance,
        'render': render,
        'generated_at': _today()
    }

def _build_objective_signals():
    """Build objective signals from existing reports"""
    signals = {}
    
    # Check for existing reports
    reports = [
        'builder/cache/schema.json',
        'builder/cache/markdownlint.json',
        'builder/cache/cspell.json'
    ]
    
    for report_path in reports:
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    report_name = os.path.basename(report_path).replace('.json', '')
                    signals[report_name] = data
            except Exception:
                continue
    
    return signals

def _build_provenance(selected_items, overflow_items, budget_summary):
    """Build provenance information"""
    return {
        'selected_count': len(selected_items),
        'overflow_count': len(overflow_items),
        'budget_utilization': sum(item.token_estimate for item in selected_items),
        'budget_summary': budget_summary,
        'selection_method': 'graph_based',
        'budget_method': 'token_aware'
    }

def _build_render_info(target_path, purpose, feature, selected_items):
    """Build render information for context generation"""
    return {
        'system': f"Context builder for {target_path}",
        'instructions': f"Generate {purpose} for {target_path}",
        'user': f"Feature: {feature or 'general'}",
        'references': [item.source_anchor for item in selected_items]
    }

def _generate_enhanced_context_md(context_package):
    """Generate enhanced context.md with pretty formatting"""
    
    task = context_package['task']
    constraints = context_package['constraints']
    
    md_parts = [
        "# Context Package",
        "",
        f"**Target**: `{task['target_path']}`",
        f"**Purpose**: {task['purpose']}",
        f"**Feature**: {task['feature'] or 'None'}",
        f"**Generated**: {context_package['generated_at']}",
        "",
        "---",
        "",
        "## Task",
        "",
        f"- **Purpose**: {task['purpose']}",
        f"- **Target Path**: `{task['target_path']}`",
        f"- **Feature**: {task['feature'] or 'None'}",
        "",
        "---",
        "",
        "## Constraints",
        "",
        "### Rules",
        "",
        constraints['rules_md'] or "No rules found",
        "",
        f"**Token Budget**: {constraints['token_limit']} tokens",
        ""
    ]
    
    # Add acceptance criteria
    if context_package['acceptance']:
        md_parts.extend([
            "---",
            "",
            "## Acceptance Criteria",
            ""
        ])
        for item in context_package['acceptance']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                item['content'],
                ""
            ])
    
    # Add decisions (ADRs)
    if context_package['decisions']:
        md_parts.extend([
            "---",
            "",
            "## Decisions (ADRs)",
            ""
        ])
        for item in context_package['decisions']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                item['content'],
                ""
            ])
    
    # Add integrations
    if context_package['integrations']:
        md_parts.extend([
            "---",
            "",
            "## Integrations",
            ""
        ])
        for item in context_package['integrations']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                item['content'],
                ""
            ])
    
    # Add architecture
    if context_package['architecture']:
        md_parts.extend([
            "---",
            "",
            "## Architecture",
            ""
        ])
        for item in context_package['architecture']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                item['content'],
                ""
            ])
    
    # Add UX
    if context_package['ux']:
        md_parts.extend([
            "---",
            "",
            "## UX",
            ""
        ])
        for item in context_package['ux']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                item['content'],
                ""
            ])
    
    # Add code
    if context_package['code']:
        md_parts.extend([
            "---",
            "",
            "## Code",
            ""
        ])
        for item in context_package['code']:
            md_parts.extend([
                f"### {item['title']}",
                "",
                f"*Source: {item['source_anchor']}*",
                "",
                "```typescript",
                item['content'],
                "```",
                ""
            ])
    
    # Add objective signals
    if context_package['objective_signals']:
        md_parts.extend([
            "---",
            "",
            "## Objective Signals",
            ""
        ])
        for signal_name, signal_data in context_package['objective_signals'].items():
            md_parts.extend([
                f"### {signal_name.title()}",
                "",
                f"```json",
                json.dumps(signal_data, indent=2),
                "```",
                ""
            ])
    
    # Add provenance
    provenance = context_package['provenance']
    md_parts.extend([
        "---",
        "",
        "## Provenance",
        "",
        f"- **Selected Items**: {provenance['selected_count']}",
        f"- **Overflow Items**: {provenance['overflow_count']}",
        f"- **Budget Utilization**: {provenance['budget_utilization']} tokens",
        f"- **Selection Method**: {provenance['selection_method']}",
        f"- **Budget Method**: {provenance['budget_method']}",
        ""
    ])
    
    return '\n'.join(md_parts)

def _show_context_summary(context_package, budget_summary, token_limit):
    """Show enhanced context summary"""
    task = context_package['task']
    provenance = context_package['provenance']
    
    click.echo(f"\n📦 Enhanced Context Package Summary:")
    click.echo(f"  Target: {task['target_path']}")
    click.echo(f"  Purpose: {task['purpose']}")
    click.echo(f"  Feature: {task['feature'] or 'None'}")
    click.echo(f"  Selected items: {provenance['selected_count']}")
    click.echo(f"  Overflow items: {provenance['overflow_count']}")
    click.echo(f"  Token usage: {provenance['budget_utilization']}/{token_limit}")
    
    # Show per-type breakdown
    click.echo(f"\n📊 Content by Type:")
    for content_type in ['acceptance', 'decisions', 'integrations', 'architecture', 'ux', 'code']:
        count = len(context_package.get(content_type, []))
        if count > 0:
            click.echo(f"  {content_type.title()}: {count} items")
    
    # Show budget utilization
    total_budget = sum(summary['budget_limit'] for summary in budget_summary.values())
    used_budget = sum(summary['used_tokens'] for summary in budget_summary.values())
    utilization = (used_budget / total_budget * 100) if total_budget > 0 else 0
    
    click.echo(f"\n💰 Budget Utilization: {utilization:.1f}%")
    
    if utilization > 100:
        click.echo(f"⚠️  Budget exceeded!")
    elif utilization > 80:
        click.echo(f"⚠️  Approaching budget limit")
    else:
        click.echo(f"✅ Budget usage within limits")

# -------------------- DOCUMENT LINKS --------------------
@cli.command("doc:set-links")
@click.argument("file")
@click.option("--prd", default=None)
@click.option("--arch", default=None)
@click.option("--adr", default=None)
@click.option("--impl", default=None)
@click.option("--exec", "exec_", default=None)
@click.option("--ux", default=None)
def doc_set_links(file, prd, arch, adr, impl, exec_, ux):
    """Set front-matter links on a doc without manual editing."""
    fm, txt, m = _doc_load_front_matter(file)
    if m is None:
        raise click.ClickException(f"No YAML front-matter found in {file}")
    links = fm.get("links") or {}
    if prd: links["prd"] = prd
    if arch: links["arch"] = arch
    if adr: links["adr"] = adr
    if impl: links["impl"] = impl
    if exec_: links["exec"] = exec_
    if ux: links["ux"] = ux
    fm["links"] = links
    _doc_save_front_matter(file, fm, txt, m)
    click.echo(f"Updated links in {file}: " + ", ".join([f"{k}={v}" for k,v in links.items()]))

# -------------------- DOCUMENT VALIDATOR --------------------
@cli.command("doc:check")
@click.option("--output", default="builder/cache/schema.json", help="Output JSON report path")
@click.option("--fail-fast", is_flag=True, help="Stop on first validation error")
def doc_check(output, fail_fast):
    """Validate docs front-matter and required sections; write builder/cache/schema.json."""
    import subprocess, sys, os
    ROOT = os.path.dirname(os.path.dirname(__file__))
    rc = subprocess.call([sys.executable, os.path.join(ROOT,"builder","evaluators","doc_schema.py")])
    sys.exit(rc)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    if os.path.isfile(path):
        # Validate single file
        click.echo(f"🔍 Validating single file: {path}")
        result = validate_document_file(path)
        
        if result['valid']:
            click.echo(f"✅ {path} is valid")
            if result['warnings']:
                click.echo("⚠️  Warnings:")
                for warning in result['warnings']:
                    click.echo(f"  - {warning}")
        else:
            click.echo(f"❌ {path} is invalid")
            click.echo("Errors:")
            for error in result['errors']:
                click.echo(f"  - {error}")
            if fail_fast:
                raise SystemExit(1)
        
        # Save single file report
        report = {
            'summary': {
                'total_files': 1,
                'valid_files': 1 if result['valid'] else 0,
                'invalid_files': 0 if result['valid'] else 1,
                'validation_rate': 1.0 if result['valid'] else 0.0
            },
            'results': [result]
        }
        
    elif os.path.isdir(path):
        # Validate directory
        click.echo(f"🔍 Validating directory: {path}")
        report = validate_documents_in_directory(path)
        
        # Show summary
        summary = report['summary']
        click.echo(f"\n📊 Validation Summary:")
        click.echo(f"  Total files: {summary['total_files']}")
        click.echo(f"  Valid files: {summary['valid_files']}")
        click.echo(f"  Invalid files: {summary['invalid_files']}")
        click.echo(f"  Validation rate: {summary['validation_rate']:.1%}")
        
        # Show errors for invalid files
        invalid_files = [r for r in report['results'] if not r['valid']]
        if invalid_files:
            click.echo(f"\n❌ Invalid files:")
            for result in invalid_files:
                click.echo(f"  {result['file_path']}:")
                for error in result['errors']:
                    click.echo(f"    - {error}")
            if fail_fast:
                raise SystemExit(1)
        
        # Show warnings
        files_with_warnings = [r for r in report['results'] if r['warnings']]
        if files_with_warnings:
            click.echo(f"\n⚠️  Files with warnings:")
            for result in files_with_warnings:
                click.echo(f"  {result['file_path']}:")
                for warning in result['warnings']:
                    click.echo(f"    - {warning}")
    
    else:
        click.echo(f"❌ Path not found: {path}")
        raise SystemExit(1)
    
    # Save report
    try:
        save_schema_report(report, output)
        click.echo(f"\n✅ Report saved to: {output}")
    except Exception as e:
        click.echo(f"❌ Error saving report: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT GRAPH --------------------
@cli.command("context:scan")
@click.option("--output", default="builder/cache/context_graph.json", help="Output JSON file path")
@click.option("--stats-only", is_flag=True, help="Only print statistics, don't export JSON")
def context_scan(output, stats_only):
    """Scan project and build context graph of nodes and relationships"""
    try:
        from context_graph import ContextGraph
        
        click.echo("🔍 Scanning project for context graph...")
        
        # Build context graph
        graph = ContextGraph()
        graph.scan_project(ROOT)
        
        # Print statistics
        graph.print_stats()
        
        # Export to JSON unless stats-only
        if not stats_only:
            os.makedirs(os.path.dirname(output), exist_ok=True)
            graph.export_json(output)
            click.echo(f"📁 Context graph exported to: {output}")
        
    except ImportError as e:
        click.echo(f"❌ Import error: {e}")
        click.echo("Make sure context_graph.py exists in the builder directory")
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT SELECTION --------------------
@cli.command("context:select")
@click.argument("start_path", required=False)
@click.option("--feature", help="Start from a specific feature")
@click.option("--max-items", default=10, help="Maximum number of items to return")
@click.option("--max-distance", default=2, help="Maximum distance (hops) to follow")
@click.option("--summary-only", is_flag=True, help="Only show summary, not detailed results")
def context_select(start_path, feature, max_items, max_distance, summary_only):
    """Select and rank relevant context items from a starting path or feature"""
    try:
        from context_select import ContextSelector
        import json
        
        # Load context graph
        context_graph_path = os.path.join(ROOT, "builder", "cache", "context_graph.json")
        if not os.path.exists(context_graph_path):
            click.echo("❌ Context graph not found. Run 'context:scan' first.")
            raise SystemExit(1)
            
        # Load graph from JSON
        with open(context_graph_path, 'r') as f:
            graph_data = json.load(f)
            
        # Reconstruct graph
        from context_graph import ContextGraph, GraphNode, GraphEdge
        graph = ContextGraph()
        
        for node_data in graph_data['nodes']:
            node = GraphNode(
                id=node_data['id'],
                node_type=node_data['type'],
                title=node_data['title'],
                file_path=node_data['file_path'],
                metadata=node_data['metadata'],
                properties=node_data['properties']
            )
            graph.add_node(node)
            
        for edge_data in graph_data['edges']:
            edge = GraphEdge(
                source_id=edge_data['source'],
                target_id=edge_data['target'],
                edge_type=edge_data['type'],
                weight=edge_data.get('weight', 1.0),
                metadata=edge_data.get('metadata', {})
            )
            graph.add_edge(edge)
            
        # Create selector and get context
        selector = ContextSelector(graph)
        
        if start_path:
            click.echo(f"🔍 Selecting context for path: {start_path}")
        if feature:
            click.echo(f"🔍 Selecting context for feature: {feature}")
            
        items = selector.select_context(start_path, feature, max_items, max_distance)
        
        if not items:
            click.echo("❌ No relevant context found")
            return
            
        # Print results
        if not summary_only:
            click.echo(f"\n📊 Found {len(items)} relevant items:")
            click.echo("=" * 60)
            
            for i, item in enumerate(items, 1):
                click.echo(f"{i:2d}. {item}")
                if item.reasons:
                    click.echo(f"     Reasons: {', '.join(item.reasons)}")
                click.echo()
                
        # Print summary
        summary = selector.get_context_summary(items)
        click.echo("📈 Summary:")
        click.echo(f"  Total items: {summary['total_items']}")
        click.echo(f"  By type: {summary['by_type']}")
        click.echo(f"  By feature: {summary['by_feature']}")
        click.echo(f"  By distance: {summary['by_distance']}")
        if summary['total_items'] > 0:
            click.echo(f"  Score range: {summary['score_range']['min']:.1f} - {summary['score_range']['max']:.1f} (avg: {summary['score_range']['avg']:.1f})")
        
    except ImportError as e:
        click.echo(f"❌ Import error: {e}")
        click.echo("Make sure context_select.py exists in the builder directory")
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- ENHANCED CONTEXT BUILD --------------------
@cli.command("ctx:build-enhanced")
@click.argument("target_path")
@click.option("--purpose", required=True, help="Purpose: implement, review, test, etc.")
@click.option("--feature", default="", help="Feature name for rules")
@click.option("--stacks", default="typescript,react", help="Comma-separated stack names")
@click.option("--token-limit", default=8000, help="Token budget limit")
def ctx_build_enhanced(target_path, purpose, feature, stacks, token_limit):
    """Build enhanced context package using graph + selection + budget"""
    try:
        from context_graph import ContextGraphBuilder
        from context_select import ContextSelector
        from context_budget import ContextBudgetManager
        
        # Ensure cache directory exists
        os.makedirs(CACHE, exist_ok=True)
        
        click.echo(f"🔍 Building enhanced context for: {target_path}")
        click.echo(f"📋 Purpose: {purpose}, Feature: {feature or 'None'}")
        click.echo(f"💰 Token budget: {token_limit}")
        
        # Step 1: Build context graph
        click.echo("📊 Building context graph...")
        graph_builder = ContextGraphBuilder(ROOT)
        graph = graph_builder.build()
        
        # Step 2: Select context using graph
        click.echo("🎯 Selecting relevant context...")
        selector = ContextSelector(ROOT)
        context_selection = selector.select_context(target_path, feature, top_k=10)
        
        if not context_selection:
            click.echo("❌ No context found for target path")
            return
        
        # Step 3: Apply budget constraints
        click.echo("💰 Applying token budget...")
        budget_manager = ContextBudgetManager(total_budget=token_limit)
        budget_items = budget_manager.create_budget_items(context_selection)
        selected_items, overflow_items, budget_summary = budget_manager.apply_budget(budget_items)
        
        # Step 4: Load rules
        rules = _load_rules(feature, stacks)
        
        # Step 5: Build enhanced context package
        context_package = _build_enhanced_context_package(
            target_path, purpose, feature, stacks, token_limit,
            selected_items, overflow_items, budget_summary, rules
        )
        
        # Step 6: Write pack_context.json
        pack_context_path = os.path.join(CACHE, "pack_context.json")
        with open(pack_context_path, "w", encoding="utf-8") as f:
            json.dump(context_package, f, indent=2, ensure_ascii=False)
        click.echo(f"✅ Created {pack_context_path}")
        
        # Step 7: Generate enhanced context.md
        context_md = _generate_enhanced_context_md(context_package)
        context_md_path = os.path.join(CACHE, "context.md")
        with open(context_md_path, "w", encoding="utf-8") as f:
            f.write(context_md)
        click.echo(f"✅ Created {context_md_path}")
        
        # Step 8: Show summary
        _show_context_summary(context_package, budget_summary, token_limit)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT BUDGET --------------------
@cli.command("context:budget")
@click.argument("start_path", required=False)
@click.option("--feature", help="Start from a specific feature")
@click.option("--token-limit", default=8000, help="Total token budget limit")
@click.option("--max-items", default=20, help="Maximum number of context items to consider")
@click.option("--output", default="builder/cache/context_package.md", help="Output file path")
def context_budget(start_path, feature, token_limit, max_items, output):
    """Build a token-aware context package with budget management"""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        from context_budget import ContextBudgetManager
        from context_select import ContextSelector
        import json
        
        # Load context graph
        context_graph_path = os.path.join(ROOT, "builder", "cache", "context_graph.json")
        if not os.path.exists(context_graph_path):
            click.echo("❌ Context graph not found. Run 'context:scan' first.")
            raise SystemExit(1)
            
        # Load graph from JSON
        with open(context_graph_path, 'r') as f:
            graph_data = json.load(f)
            
        # Reconstruct graph
        from context_graph import ContextGraph, GraphNode, GraphEdge
        graph = ContextGraph()
        
        for node_data in graph_data['nodes']:
            node = GraphNode(
                id=node_data['id'],
                node_type=node_data['type'],
                title=node_data['title'],
                file_path=node_data['file_path'],
                metadata=node_data['metadata'],
                properties=node_data['properties']
            )
            graph.add_node(node)
            
        for edge_data in graph_data['edges']:
            edge = GraphEdge(
                source_id=edge_data['source'],
                target_id=edge_data['target'],
                edge_type=edge_data['type'],
                weight=edge_data.get('weight', 1.0),
                metadata=edge_data.get('metadata', {})
            )
            graph.add_edge(edge)
            
        # Create budget manager
        budget_manager = ContextBudgetManager(token_limit)
        
        # Get context items
        selector = ContextSelector(graph)
        items = selector.select_context(start_path, feature, max_items)
        
        if not items:
            click.echo("❌ No relevant context found")
            return
            
        click.echo(f"🔍 Building context package with {len(items)} items")
        click.echo(f"📊 Token limit: {token_limit}")
        
        # Build context package
        context_package = budget_manager.build_context_package(items)
        
        # Print summary
        summary = budget_manager.get_usage_summary()
        click.echo(f"\n📈 Budget Usage Summary:")
        click.echo(f"  Total used: {summary['total_used']}/{summary['total_allocated']}")
        click.echo(f"  Over budget: {summary['is_over_budget']}")
        click.echo()
        
        for category, cat_summary in summary['categories'].items():
            status = "⚠️" if cat_summary['is_over_budget'] else "✅"
            click.echo(f"  {status} {category}: {cat_summary['used']}/{cat_summary['allocated']} tokens ({cat_summary['item_count']} items)")
            
        # Save context package
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, 'w') as f:
            f.write(context_package)
        click.echo(f"\n📁 Context package saved to: {output}")
        
    except ImportError as e:
        click.echo(f"❌ Import error: {e}")
        click.echo("Make sure context_budget.py exists in the builder directory")
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

@cli.command("ctx:explain")
@click.option("--target-path", default="", help="Target path to explain context for")
@click.option("--feature", default="", help="Feature name to explain context for")
@click.option("--max-items", default=20, help="Maximum number of items to show")
def ctx_explain(target_path, feature, max_items):
    """Explain context selection with ranked table showing source, type, weight, reason, status, mtime."""
    try:
        from context_graph import ContextGraph, GraphNode, GraphEdge
        from context_select import ContextSelector
        import json
        from datetime import datetime
        
        # Load context graph
        context_graph_path = os.path.join(CACHE, "context_graph.json")
        if not os.path.exists(context_graph_path):
            click.echo("❌ No context graph found. Run 'ctx:build' first.")
            raise SystemExit(1)
            
        with open(context_graph_path, 'r') as f:
            graph_data = json.load(f)
        
        # Reconstruct graph
        graph = ContextGraph()
        for node_data in graph_data['nodes']:
            node = GraphNode(
                id=node_data['id'],
                node_type=node_data['type'],
                title=node_data['title'],
                file_path=node_data['file_path'],
                metadata=node_data.get('metadata', {}),
                properties=node_data.get('properties', {})
            )
            graph.add_node(node)
        
        for edge_data in graph_data['edges']:
            edge = GraphEdge(
                source_id=edge_data['source'],
                target_id=edge_data['target'],
                edge_type=edge_data.get('edge_type', 'informs'),
                weight=edge_data.get('weight', 1.0),
                metadata=edge_data.get('metadata', {})
            )
            graph.add_edge(edge)
        
        # Create context selector
        selector = ContextSelector(graph)
        
        # Select context items
        if target_path:
            items = selector.select_context(start_path=target_path, max_items=max_items)
        elif feature:
            items = selector.select_context(start_feature=feature, max_items=max_items)
        else:
            # If no specific target, use the first available node as starting point
            if not graph.nodes:
                click.echo("❌ No nodes found in context graph.")
                return
            first_node = list(graph.nodes.values())[0]
            items = selector.select_context(start_path=first_node.file_path, max_items=max_items)
        
        if not items:
            click.echo("❌ No context items found.")
            return
        
        # Display ranked table
        click.echo("📊 Context Selection Explanation")
        click.echo("=" * 80)
        click.echo(f"{'Rank':<4} {'Source':<30} {'Type':<8} {'Weight':<8} {'Status':<10} {'MTime':<12} {'Reasons'}")
        click.echo("-" * 80)
        
        for i, item in enumerate(items, 1):
            # Get file modification time
            mtime = "N/A"
            if item.node.file_path and os.path.exists(item.node.file_path):
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(item.node.file_path)).strftime("%Y-%m-%d")
                except:
                    mtime = "N/A"
            
            # Get status from metadata
            status = item.node.metadata.get('status', 'unknown')
            
            # Get source (filename or title)
            source = os.path.basename(item.node.file_path) if item.node.file_path else item.node.title
            if len(source) > 28:
                source = source[:25] + "..."
            
            # Format reasons
            reasons = ", ".join(item.reasons) if item.reasons else "N/A"
            if len(reasons) > 40:
                reasons = reasons[:37] + "..."
            
            click.echo(f"{i:<4} {source:<30} {item.node.node_type:<8} {item.score:<8.1f} {status:<10} {mtime:<12} {reasons}")
        
        click.echo(f"\n📈 Total items: {len(items)}")
        click.echo(f"🎯 Target: {target_path or feature or 'all items'}")
        
    except ImportError as e:
        click.echo(f"❌ Import error: {e}")
        click.echo("Make sure context modules exist in the builder directory")
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

@cli.command("ctx:pack")
@click.option("--output", default="", help="Output file path (prints to stdout if not specified)")
def ctx_pack(output):
    """Emit 4 blocks (system, instructions, user, references) from pack_context.json; respect budgets."""
    try:
        import json
        
        # Load pack_context.json
        pack_context_path = os.path.join(CACHE, "pack_context.json")
        if not os.path.exists(pack_context_path):
            click.echo("❌ No pack_context.json found. Run 'ctx:build' first.")
            raise SystemExit(1)
            
        with open(pack_context_path, 'r') as f:
            context_package = json.load(f)
        
        # Build the 4 blocks
        blocks = []
        
        # Block 1: System (Rules and Guardrails - should lead)
        system_block = []
        system_block.append("## SYSTEM")
        system_block.append("")
        
        # Add rules (highest priority)
        if context_package.get('rules', {}).get('rules_markdown'):
            system_block.append("### Rules")
            system_block.append("")
            system_block.append(context_package['rules']['rules_markdown'])
            system_block.append("")
        
        # Add guardrails
        if context_package.get('rules', {}).get('guardrails'):
            guardrails = context_package['rules']['guardrails']
            system_block.append("### Guardrails")
            system_block.append("")
            
            if guardrails.get('forbiddenPatterns'):
                system_block.append("#### Forbidden Patterns")
                for pattern in guardrails['forbiddenPatterns']:
                    system_block.append(f"- **Pattern**: `{pattern['pattern']}`")
                    system_block.append(f"  **Message**: {pattern['message']}")
                system_block.append("")
            
            if guardrails.get('hints'):
                system_block.append("#### Hints")
                for hint in guardrails['hints']:
                    system_block.append(f"- **Pattern**: `{hint['pattern']}`")
                    system_block.append(f"  **Message**: {hint['message']}")
                system_block.append("")
        
        blocks.append("\n".join(system_block))
        
        # Block 2: Instructions (Purpose, Feature, Stacks)
        instructions_block = []
        instructions_block.append("## INSTRUCTIONS")
        instructions_block.append("")
        
        # Purpose
        purpose = context_package.get('purpose', 'unknown')
        instructions_block.append(f"**Purpose**: {purpose}")
        instructions_block.append("")
        
        # Feature
        feature = context_package.get('feature', '')
        if feature:
            instructions_block.append(f"**Feature**: {feature}")
            instructions_block.append("")
        
        # Stacks
        stacks = context_package.get('stacks', [])
        if stacks:
            instructions_block.append(f"**Technology Stack**: {', '.join(stacks)}")
            instructions_block.append("")
        
        # PRD content if available
        if context_package.get('prd', {}).get('content'):
            instructions_block.append("### Product Requirements")
            instructions_block.append("")
            instructions_block.append(context_package['prd']['content'])
            instructions_block.append("")
        
        blocks.append("\n".join(instructions_block))
        
        # Block 3: User (Target Path and User Context)
        user_block = []
        user_block.append("## USER")
        user_block.append("")
        
        # Target path
        target_path = context_package.get('target_path', '')
        if target_path:
            user_block.append(f"**Target Path**: `{target_path}`")
            user_block.append("")
        
        # Code excerpts
        code_excerpts = context_package.get('code_excerpts', [])
        if code_excerpts:
            user_block.append("### Current Code")
            user_block.append("")
            for excerpt in code_excerpts:
                user_block.append(f"**File**: `{excerpt['path']}`")
                user_block.append("```typescript")
                user_block.append(excerpt['excerpt'])
                user_block.append("```")
                user_block.append("")
        
        # Test excerpts
        test_excerpts = context_package.get('test_excerpts', [])
        if test_excerpts:
            user_block.append("### Current Tests")
            user_block.append("")
            for excerpt in test_excerpts:
                user_block.append(f"**File**: `{excerpt['path']}`")
                user_block.append("```typescript")
                user_block.append(excerpt['excerpt'])
                user_block.append("```")
                user_block.append("")
        
        blocks.append("\n".join(user_block))
        
        # Block 4: References (ADRs, Acceptance Criteria)
        references_block = []
        references_block.append("## REFERENCES")
        references_block.append("")
        
        # Acceptance Criteria (should be present)
        acceptance_criteria = context_package.get('acceptance_criteria', [])
        if acceptance_criteria:
            references_block.append("### Acceptance Criteria")
            references_block.append("")
            for criterion in acceptance_criteria:
                references_block.append(f"- {criterion}")
            references_block.append("")
        
        # ADRs
        adrs = context_package.get('adrs', [])
        if adrs:
            references_block.append("### Architecture Decision Records")
            references_block.append("")
            for i, adr in enumerate(adrs, 1):
                references_block.append(f"#### ADR {i}")
                references_block.append("")
                references_block.append(adr)
                references_block.append("")
        
        blocks.append("\n".join(references_block))
        
        # Combine all blocks
        full_output = "\n\n".join(blocks)
        
        # Output to file or stdout
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(full_output)
            click.echo(f"✅ Context pack saved to: {output}")
        else:
            click.echo(full_output)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

@cli.command("ctx:trace")
@click.option("--output", default="builder/cache/trace.csv", help="Output CSV file path")
@click.option("--format", type=click.Choice(['csv', 'md']), default='csv', help="Output format (csv or md)")
def ctx_trace(output, format):
    """Generate traceability matrix mapping PRD → Arch → Impl → Tasks → Code/Tests → ADRs."""
    try:
        import json
        import csv
        from collections import defaultdict
        
        # Load context graph
        context_graph_path = os.path.join(CACHE, "context_graph.json")
        if not os.path.exists(context_graph_path):
            click.echo("❌ No context graph found. Run 'context:scan' first.")
            raise SystemExit(1)
            
        with open(context_graph_path, 'r') as f:
            graph_data = json.load(f)
        
        # Build node lookup by ID
        nodes_by_id = {}
        for node in graph_data['nodes']:
            nodes_by_id[node['id']] = node
        
        # Build relationships from links metadata
        relationships = defaultdict(list)
        
        for node in graph_data['nodes']:
            node_id = node['id']
            node_type = node['type']
            metadata = node.get('metadata', {})
            links = metadata.get('links', [])
            
            # Extract relationships from links
            for link_group in links:
                for link_type, target_ids in link_group.items():
                    if target_ids:  # Only process non-empty lists
                        for target_id in target_ids:
                            if target_id in nodes_by_id:
                                relationships[node_id].append({
                                    'target': target_id,
                                    'type': link_type,
                                    'source_type': node_type,
                                    'target_type': nodes_by_id[target_id]['type']
                                })
        
        # Build traceability matrix
        trace_matrix = []
        
        # Process each PRD and trace through the hierarchy
        prd_nodes = [node for node in graph_data['nodes'] if node['type'] == 'prd']
        
        if not prd_nodes:
            click.echo("❌ No PRD documents found in context graph.")
            return
        
        for prd in prd_nodes:
            prd_id = prd['id']
            prd_title = prd['title']
            
            # Find architecture documents linked to this PRD
            arch_docs = []
            for rel in relationships.get(prd_id, []):
                if rel['type'] == 'arch' and rel['target_type'] == 'arch':
                    arch_docs.append(rel['target'])
            
            # If no direct arch links, find any arch documents
            if not arch_docs:
                arch_docs = [node['id'] for node in graph_data['nodes'] if node['type'] == 'arch']
            
            for arch_id in arch_docs:
                arch_title = nodes_by_id[arch_id]['title']
                
                # Find implementation documents linked to this arch
                impl_docs = []
                for rel in relationships.get(arch_id, []):
                    if rel['type'] == 'impl' and rel['target_type'] == 'impl':
                        impl_docs.append(rel['target'])
                
                # If no direct impl links, find any impl documents
                if not impl_docs:
                    impl_docs = [node['id'] for node in graph_data['nodes'] if node['type'] == 'impl']
                
                # If no impl docs, use ux docs as implementation guidance
                if not impl_docs:
                    impl_docs = [node['id'] for node in graph_data['nodes'] if node['type'] == 'ux']
                
                for impl_id in impl_docs:
                    impl_title = nodes_by_id[impl_id]['title']
                    
                    # Find task/execution documents
                    task_docs = []
                    for rel in relationships.get(impl_id, []):
                        if rel['type'] == 'exec' and rel['target_type'] == 'exec':
                            task_docs.append(rel['target'])
                    
                    # If no task docs, find any exec documents
                    if not task_docs:
                        task_docs = [node['id'] for node in graph_data['nodes'] if node['type'] == 'exec']
                    
                    # If no exec docs, create a placeholder
                    if not task_docs:
                        task_docs = ['TASK-PLACEHOLDER']
                    
                    for task_id in task_docs:
                        task_title = "Task Placeholder" if task_id == 'TASK-PLACEHOLDER' else nodes_by_id[task_id]['title']
                        
                        # Find code files related to this task/impl
                        code_files = []
                        test_files = []
                        
                        # Look for code files that might be related
                        for node in graph_data['nodes']:
                            if node['type'] == 'code':
                                file_path = node['file_path']
                                if file_path:
                                    if file_path.endswith('.test.ts') or file_path.endswith('.test.js'):
                                        test_files.append(node['id'])
                                    else:
                                        code_files.append(node['id'])
                        
                        # Find ADRs related to this implementation
                        adr_docs = []
                        for node in graph_data['nodes']:
                            if node['type'] == 'adr' and node['id'] != 'ADR-0000':  # Skip master ADR
                                # Check if ADR is related to any of our code files
                                metadata = node.get('metadata', {})
                                related_files = metadata.get('related_files', [])
                                if any(code_file in related_files for code_file in code_files):
                                    adr_docs.append(node['id'])
                        
                        # If no specific ADR links, include all ADRs
                        if not adr_docs:
                            adr_docs = [node['id'] for node in graph_data['nodes'] if node['type'] == 'adr' and node['id'] != 'ADR-0000']
                        
                        # Create traceability entries
                        for code_id in code_files:
                            code_title = nodes_by_id[code_id]['title']
                            code_path = nodes_by_id[code_id]['file_path']
                            
                            for adr_id in adr_docs:
                                adr_title = nodes_by_id[adr_id]['title']
                                
                                trace_matrix.append({
                                    'PRD': prd_title,
                                    'Architecture': arch_title,
                                    'Implementation': impl_title,
                                    'Tasks': task_title,
                                    'Code': code_title,
                                    'Code_Path': code_path,
                                    'Tests': ', '.join([nodes_by_id[tid]['title'] for tid in test_files if tid in nodes_by_id]),
                                    'ADRs': adr_title,
                                    'Status': 'Active'
                                })
        
        if not trace_matrix:
            click.echo("❌ No traceability relationships found.")
            return
        
        # Output the matrix
        if format == 'csv':
            # Ensure output directory exists
            output_dir = os.path.dirname(output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['PRD', 'Architecture', 'Implementation', 'Tasks', 'Code', 'Code_Path', 'Tests', 'ADRs', 'Status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(trace_matrix)
            
            click.echo(f"✅ Traceability matrix saved to: {output}")
            click.echo(f"📊 Generated {len(trace_matrix)} traceability entries")
            
        elif format == 'md':
            # Generate markdown table
            md_content = []
            md_content.append("# Traceability Matrix")
            md_content.append("")
            md_content.append("| PRD | Architecture | Implementation | Tasks | Code | Tests | ADRs | Status |")
            md_content.append("|-----|-------------|---------------|-------|------|-------|------|--------|")
            
            for entry in trace_matrix:
                md_content.append(f"| {entry['PRD']} | {entry['Architecture']} | {entry['Implementation']} | {entry['Tasks']} | {entry['Code']} | {entry['Tests']} | {entry['ADRs']} | {entry['Status']} |")
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_content))
            
            click.echo(f"✅ Traceability matrix saved to: {output}")
            click.echo(f"📊 Generated {len(trace_matrix)} traceability entries")
        
        # Show summary
        click.echo(f"\n📈 Summary:")
        click.echo(f"  PRDs: {len(set(entry['PRD'] for entry in trace_matrix))}")
        click.echo(f"  Architecture docs: {len(set(entry['Architecture'] for entry in trace_matrix))}")
        click.echo(f"  Implementation docs: {len(set(entry['Implementation'] for entry in trace_matrix))}")
        click.echo(f"  Code files: {len(set(entry['Code'] for entry in trace_matrix))}")
        click.echo(f"  ADRs: {len(set(entry['ADRs'] for entry in trace_matrix))}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT GRAPH --------------------
@cli.command("ctx:graph:build")
@click.option("--output", default="builder/cache/context_graph.json", help="Output JSON file path")
def ctx_graph_build(output):
    """Build context graph from docs and source code"""
    try:
        from context_graph import ContextGraphBuilder
        
        click.echo("🔍 Building context graph...")
        builder = ContextGraphBuilder(ROOT)
        graph = builder.build()
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Save graph
        graph.save(output)
        
        # Show stats
        stats = graph.get_stats()
        click.echo(f"✅ Context graph saved to: {output}")
        click.echo(f"📊 Graph Statistics:")
        click.echo(f"  Total nodes: {stats['total_nodes']}")
        click.echo(f"  Total edges: {stats['total_edges']}")
        click.echo(f"  Node types: {stats['node_counts']}")
        click.echo(f"  Edge types: {stats['edge_counts']}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

@cli.command("ctx:graph:stats")
def ctx_graph_stats():
    """Show context graph statistics"""
    try:
        from context_graph import ContextGraphBuilder
        
        # Build or load graph
        graph_file = os.path.join(ROOT, "builder", "cache", "context_graph.json")
        if os.path.exists(graph_file):
            from context_graph import ContextGraph
            graph = ContextGraph.load(graph_file)
            click.echo("📊 Context Graph Statistics (from cache):")
        else:
            click.echo("🔍 Building context graph...")
            builder = ContextGraphBuilder(ROOT)
            graph = builder.build()
            click.echo("📊 Context Graph Statistics (fresh build):")
        
        stats = graph.get_stats()
        
        # Display stats
        click.echo(f"  Total nodes: {stats['total_nodes']}")
        click.echo(f"  Total edges: {stats['total_edges']}")
        click.echo("")
        
        click.echo("  Node counts by type:")
        for node_type, count in sorted(stats['node_counts'].items()):
            click.echo(f"    {node_type}: {count}")
        
        click.echo("")
        click.echo("  Edge counts by type:")
        for edge_type, count in sorted(stats['edge_counts'].items()):
            click.echo(f"    {edge_type}: {count}")
        
        # Show some sample relationships
        if stats['total_edges'] > 0:
            click.echo("")
            click.echo("  Sample relationships:")
            sample_count = 0
            for from_node, edges in graph.edges.items():
                if sample_count >= 5:
                    break
                for edge in edges[:2]:  # Show first 2 edges from each node
                    if sample_count >= 5:
                        break
                    from_info = graph.get_node(from_node)
                    to_info = graph.get_node(edge['to'])
                    if from_info and to_info:
                        click.echo(f"    {from_info['type']}:{from_node} --{edge['type']}--> {to_info['type']}:{edge['to']}")
                        sample_count += 1
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT SELECTION --------------------
@cli.command("ctx:select")
@click.argument("target_path")
@click.option("--feature", default="", help="Feature name for feature-based scoring")
@click.option("--top-k", default=5, help="Number of top items to return per type")
@click.option("--output", default="builder/cache/context_selection.json", help="Output JSON file path")
def ctx_select(target_path, feature, top_k, output):
    """Select and rank context for a target path"""
    try:
        from context_select import ContextSelector
        
        click.echo(f"🔍 Selecting context for: {target_path}")
        if feature:
            click.echo(f"📋 Feature: {feature}")
        
        selector = ContextSelector(ROOT)
        context = selector.select_context(target_path, feature, top_k)
        
        if not context:
            click.echo("❌ No context found for target path")
            return
        
        # Save context selection
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False, default=str)
        
        # Show summary
        summary = selector.get_context_summary(context)
        click.echo(f"✅ Context selection saved to: {output}")
        click.echo(summary)
        
        # Show statistics
        total_items = sum(len(items) for items in context.values())
        click.echo(f"\n📊 Selected {total_items} context items across {len(context)} types")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

# -------------------- CONTEXT BUDGET --------------------
@cli.command("ctx:budget")
@click.argument("target_path")
@click.option("--feature", default="", help="Feature name for feature-based scoring")
@click.option("--budget", default=8000, help="Total token budget")
@click.option("--output", default="builder/cache/context_budget.json", help="Output JSON file path")
@click.option("--report", default="builder/cache/budget_report.md", help="Budget report markdown file path")
def ctx_budget(target_path, feature, budget, output, report):
    """Apply token budget to context selection"""
    try:
        from context_select import ContextSelector
        from context_budget import ContextBudgetManager
        
        click.echo(f"💰 Applying token budget to: {target_path}")
        click.echo(f"📊 Total budget: {budget} tokens")
        if feature:
            click.echo(f"📋 Feature: {feature}")
        
        # Get context selection
        selector = ContextSelector(ROOT)
        context = selector.select_context(target_path, feature, top_k=10)  # Get more items for budgeting
        
        if not context:
            click.echo("❌ No context found for target path")
            return
        
        # Apply budget
        budget_manager = ContextBudgetManager(total_budget=budget)
        budget_items = budget_manager.create_budget_items(context)
        selected_items, overflow_items, budget_summary = budget_manager.apply_budget(budget_items)
        
        # Save results
        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        budget_manager.save_budget_results(selected_items, overflow_items, budget_summary, output)
        
        # Generate and save report
        report_content = budget_manager.create_budget_report(selected_items, overflow_items, budget_summary)
        with open(report, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Show summary
        total_tokens = sum(item.token_estimate for item in selected_items)
        click.echo(f"✅ Budget applied successfully!")
        click.echo(f"📄 Selected: {len(selected_items)} items ({total_tokens} tokens)")
        click.echo(f"📄 Overflow: {len(overflow_items)} items")
        click.echo(f"📊 Budget utilization: {total_tokens / budget * 100:.1f}%")
        click.echo(f"💾 Results saved to: {output}")
        click.echo(f"📋 Report saved to: {report}")
        
        # Show per-type breakdown
        click.echo(f"\n📊 Budget Allocation:")
        for budget_type, summary in budget_summary.items():
            click.echo(f"  {budget_type.upper()}: {summary['selected_items']}/{summary['total_items']} items ({summary['used_tokens']}/{summary['budget_limit']} tokens)")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    cli()
