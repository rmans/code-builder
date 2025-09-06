#!/usr/bin/env python3
import os, json
from jinja2 import Template

def main():
    # Import overlay paths for dual-mode support
    try:
        from ..overlay.paths import OverlayPaths
        overlay_paths = OverlayPaths()
        ROOT = overlay_paths.get_root()
    except ImportError:
        # Fallback for standalone mode
        ROOT = os.path.dirname(os.path.dirname(__file__))
    TEMPL = os.path.join(ROOT, "docs", "templates", "spec.md.hbs")
    OUT   = os.path.join(ROOT, "docs", "SPEC_hello.md")

    with open(os.path.join(ROOT, "builder", "cache", "context.json"), "r") as f:
        ctx = json.load(f)
    ctx.update({
      "name": "hello module",
      "goal": "Provide a simple greeting.",
      "acceptance": [
        "returns a string greeting",
        "exported from the module",
        "easily testable"
      ]
    })
    with open(TEMPL, "r", encoding="utf-8") as f:
        tpl = Template(f.read())
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(tpl.render(**ctx))
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
