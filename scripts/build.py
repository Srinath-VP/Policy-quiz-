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
def load_list(name):
    f = ROOT / "data" / name
    order = json.loads(f.read_text()) if f.exists() else []
    return [json.loads((ROOT / f"data/{sid}.json").read_text(encoding="utf-8")) for sid in order]

exams = load_list("exams.json")
new_policy = load_list("new-policy.json")

def bake(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

fragment = (ROOT / "src/template.html").read_text(encoding="utf-8")
notes_file = ROOT / "data/study-notes.json"
notes = json.loads(notes_file.read_text(encoding="utf-8")) if notes_file.exists() else None

for marker, data in (("/*__POLICIES__*/[]", policies), ("/*__EXAMS__*/[]", exams),
                     ("/*__NEWPOLICY__*/[]", new_policy), ("/*__NOTES__*/null", notes)):
    assert fragment.count(marker) == 1, f"template must contain the {marker} marker exactly once"
    fragment = fragment.replace(marker, bake(data))

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
