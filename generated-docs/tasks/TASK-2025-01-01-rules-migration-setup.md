---
id: TASK-2025-01-01-rules-migration-setup
title: Setup Rules System with MDC Support (Dual-Path + Migration)
description: Migrate from docs/rules/*.md to .cursor/rules/*.mdc with backward compatibility and CLI
status: pending
created: 2025-01-15
updated: 2025-01-15
owner: rules-agent
domain: rules
priority: 20
agent_type: backend
dependencies: []
tags: [rules, migration, mdc, compatibility]
---

# Task: Setup Rules System with MDC Support

## Implementation Steps
1) Dual-path loader (builder/core/context_rules.py)

```python
# builder/core/context_rules.py
from dataclasses import dataclass
from pathlib import Path
import re, json, hashlib, yaml

@dataclass
class MdcRule:
    path: Path; fm: dict; body: str

RE_FM = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)

def token_estimate(s: str) -> int:
    # ~4 chars per token (coarse but practical)
    return max(1, len(s) // 4)

def parse_mdc(p: Path) -> MdcRule:
    raw = p.read_text(encoding="utf-8")
    m = RE_FM.match(raw);  assert m, f"Missing front-matter: {p}"
    fm = yaml.safe_load(m.group(1)) or {};  body = m.group(2).strip()
    return MdcRule(p, fm, body)

def parse_md_as_mdc(p: Path) -> MdcRule:
    # Back-compat: plain .md → wrap as MDC with minimal FM
    raw = p.read_text(encoding="utf-8")
    m = RE_FM.match(raw)
    if m:
        fm = yaml.safe_load(m.group(1)) or {}; body = m.group(2).strip()
    else:
        fm = {"description": f"Migrated from {p.name}", "globs": [], "alwaysApply": False}
        body = raw
    return MdcRule(p, fm, body)

def load_rules(prefer_new: bool=True):
    newp, oldp = Path(".cursor/rules"), Path("docs/rules")
    if prefer_new and newp.exists():
        return [parse_mdc(p) for p in sorted(newp.glob("*.mdc"))]
    if oldp.exists():
        return [parse_md_as_mdc(p) for p in sorted(oldp.glob("*.md"))]
    return []

def validate_rule(r: MdcRule) -> list[str]:
    e=[]; fm=r.fm
    if not isinstance(fm.get("description"), str): e.append("description missing/string")
    if "globs" not in fm or not (fm["globs"]==[] or isinstance(fm["globs"], list)): e.append("globs must be [] or list")
    if not isinstance(fm.get("alwaysApply", False), bool): e.append("alwaysApply must be boolean")
    if fm.get("alwaysApply") and token_estimate(r.body) > 500: e.append("Always rule over 500 tokens")
    for sec in ["## Do", "## Examples"]:
        if sec not in r.body: e.append(f"missing section: {sec}")
    return e
```

2) CLI (builder/core/cli.py)
- Add subcommands: rules:validate, rules:list, rules:migrate --backup --dry-run --validate

3) Migration: rules:migrate converts docs/rules/*.md → .cursor/rules/*.mdc (backup to .cursor/rules._backup/YYYYmmddHHMM/).

## Commands
python3 builder/core/cli.py rules:migrate --backup --validate
python3 builder/core/cli.py rules:validate
python3 builder/core/cli.py rules:list

## Acceptance Criteria
- Dual-path loading works; .mdc preferred, .md fallback
- Validator flags non-array globs & >500 token Always rules
- Migration creates backup and valid .mdc files
- Context/evaluation systems remain functional

## Testing / Verification
- Fixtures with .md only, .mdc only, mixed → correct source chosen.
- CI step runs rules:migrate --dry-run --validate.

## Rollback
- Restore from latest .cursor/rules._backup/*; revert loader to old path (single commit).
