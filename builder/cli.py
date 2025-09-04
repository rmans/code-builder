#!/usr/bin/env python3
import os, json, datetime, glob, re, fnmatch
import click
from jinja2 import Template
from pathlib import Path as PPath

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

if __name__ == "__main__":
    cli()
