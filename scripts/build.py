#!/usr/bin/env python3
"""Bake data/*.json into src/template.html.

Outputs:
  dist/index.html     full standalone page (open by double-click, or host anywhere static)
  dist/artifact.html  same page as a body fragment (for publishing as a Claude artifact)
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
subprocess.run([sys.executable, str(ROOT / "scripts/validate.py")], check=True)

order = json.loads((ROOT / "data/policies.json").read_text())
policies = [json.loads((ROOT / f"data/{pid}.json").read_text(encoding="utf-8")) for pid in order]
payload = json.dumps(policies, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

tpl = (ROOT / "src/template.html").read_text(encoding="utf-8")
marker = "/*__POLICIES__*/[]"
assert tpl.count(marker) == 1, "template must contain the POLICIES marker exactly once"
fragment = tpl.replace(marker, payload)

head_end = fragment.index("</style>") + len("</style>")
standalone = (
    "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
    + fragment[:head_end] + "\n</head>\n<body>\n" + fragment[head_end:] + "\n</body>\n</html>\n"
)

dist = ROOT / "dist"; dist.mkdir(exist_ok=True)
(dist / "index.html").write_text(standalone, encoding="utf-8")
(dist / "artifact.html").write_text(fragment, encoding="utf-8")
print(f"  built dist/index.html ({len(standalone)//1024} KB) and dist/artifact.html")
