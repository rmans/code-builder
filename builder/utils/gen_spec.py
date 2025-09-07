#!/usr/bin/env python3
import os, json
from jinja2 import Template

def main():
    # Import configuration and overlay paths for dual-mode support
    from ..config.settings import get_config
    from ..overlay.paths import OverlayPaths
    
    # Initialize configuration and paths
    config = get_config()
    overlay_paths = OverlayPaths()
    ROOT = overlay_paths.get_root()
    TEMPL = os.path.join(overlay_paths.get_templates_dir(), "spec.md.hbs")
    OUT   = os.path.join(overlay_paths.get_docs_dir(), "SPEC_hello.md")

    with open(os.path.join(overlay_paths.get_cache_dir(), "context.json"), "r") as f:
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
