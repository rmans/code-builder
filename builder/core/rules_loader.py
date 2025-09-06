#!/usr/bin/env python3
import os, json, glob

# Import overlay paths for dual-mode support
try:
    from ..overlay.paths import OverlayPaths
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
    RULES_DIR = overlay_paths.get_rules_dir()
except ImportError:
    # Fallback for standalone mode
    ROOT = os.path.dirname(os.path.dirname(__file__))
    RULES_DIR = os.path.join(ROOT, "docs", "rules")

def _read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def load_rules(feature: str | None, stacks: list[str]) -> dict:
    """
    Merge rules by precedence:
      1) feature/<feature>.md
      2) stack/*<stack>.md (first match per stack)
      3) 10-project.md
      4) 00-global.md
    Also loads guardrails.json if present.
    """
    merged_md = []

    # feature-specific (highest)
    if feature:
        fp = os.path.join(RULES_DIR, "feature", f"30-{feature}.md")
        if os.path.exists(fp):
            merged_md.append(_read(fp))

    # stack-specific
    for s in stacks or []:
        matches = sorted(glob.glob(os.path.join(RULES_DIR, "stack", f"*{s}.md")))
        if matches:
            merged_md.append(_read(matches[0]))

    # project and global
    merged_md.append(_read(os.path.join(RULES_DIR, "10-project.md")))
    merged_md.append(_read(os.path.join(RULES_DIR, "00-global.md")))

    # guardrails
    guardrails_path = os.path.join(RULES_DIR, "guardrails.json")
    guardrails = {}
    if os.path.exists(guardrails_path):
        try:
            with open(guardrails_path, "r", encoding="utf-8") as f:
                guardrails = json.load(f)
        except Exception:
            guardrails = {}

    return {
        "rules_markdown": "\n\n---\n\n".join([m for m in merged_md if m.strip()]),
        "guardrails": guardrails
    }
