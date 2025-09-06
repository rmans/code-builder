import json, re, sys
from pathlib import Path
import yaml

# Import overlay paths for dual-mode support
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = Path(overlay_paths.get_root())
except ImportError:
    # Fallback for standalone mode
    ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
CACHE = ROOT / "builder" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

REQUIRED_BASE = ["type","id","title","status","owner","created","links"]
STATUS_ENUM = {
    # Core statuses
    "draft", "review", "approved", "deprecated",
    # Execution/Implementation statuses
    "planned", "proposed", "pending", "in_progress", "accepted"
}

TYPE_SECTIONS = {
"prd": ["Problem", "Goals", "Requirements", "Metrics"],
"architecture": ["Context", "Decisions", "Architecture View", "Security", "Operability"],
"integration": ["Purpose", "Contracts", "Data Flow", "Error Handling", "Testing & Environments", "Rollout"],
"ux": ["Users", "Flows", "Screens", "Accessibility", "Content", "Components"],
"implementation": ["Plan", "Tasks", "Testing Strategy", "Performance", "Security"],
"execution": ["Milestones", "Ownership", "Rollout Plan", "Comms", "Post-launch"],
"task": ["Details", "Definition of Done"]
}

def _front_matter(text: str):
    m = re.search(r'^---\n(.*?)\n---\n', text, flags=re.S)
    if not m: return None, None, None
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except Exception:
        data = {}
    return data, m.start(), m.end()

def _has_section(md: str, name: str) -> bool:
    # simple heading match - look for ## headings
    return re.search(rf'^##\s*{re.escape(name)}\b', md, flags=re.M|re.I) is not None

def validate_file(path: Path):
    txt = path.read_text(encoding="utf-8")
    fm, s, e = _front_matter(txt)
    errs = []
    if fm is None:
        errs.append("missing front-matter")
        return {"file": str(path), "ok": False, "errors": errs}
    
    # base keys
    for k in REQUIRED_BASE:
        if k not in fm: errs.append(f"missing key: {k}")
    
    # status
    if "status" in fm and fm["status"] not in STATUS_ENUM:
        errs.append(f"invalid status: {fm['status']}")
    
    # Skip section validation for master files (0000_MASTER_*.md)
    if "0000_MASTER_" in path.name:
        return {"file": str(path), "ok": len(errs)==0, "errors": errs}
    
    # type sections
    t = fm.get("type")
    body = txt[e:] if e else ""
    wanted = TYPE_SECTIONS.get(t, [])
    for sec in wanted:
        if not _has_section(body, sec):
            errs.append(f"missing section: {sec}")
    return {"file": str(path), "ok": len(errs)==0, "errors": errs}

def run():
    out = {"results": []}
    for sub in ["prd","arch","integrations","ux","impl","exec","tasks"]:
        d = DOCS / sub
        if not d.exists(): continue
        for p in d.glob("*.md"):
            out["results"].append(validate_file(p))
    out["summary"] = {
        "errors": sum(1 for r in out["results"] if not r["ok"]),
        "files": len(out["results"])
    }
    (CACHE / "schema.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {CACHE/'schema.json'} with {out['summary']['errors']} error(s) across {out['summary']['files']} file(s)")
    return 0 if out["summary"]["errors"] == 0 else 1

if __name__ == "__main__":
    sys.exit(run())