#!/usr/bin/env python3
"""Validate every policy file in data/ before building.

Rules: <=100 quizzes per policy, exactly 10 questions per quiz, 4 distinct options,
one correct index (0-3), non-empty explanation. Also warns if the answer key is lopsided.
Exit code 1 on any error.
"""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_QUIZZES, Q_PER_QUIZ = 100, 10

def main():
    order = json.loads((ROOT / "data/policies.json").read_text())
    errors, total_q, total_z = [], 0, 0
    for pid in order:
        path = ROOT / f"data/{pid}.json"
        if not path.exists():
            errors.append(f"{pid}: listed in policies.json but data/{pid}.json is missing"); continue
        p = json.loads(path.read_text(encoding="utf-8"))
        if p.get("id") != pid: errors.append(f"{path.name}: id '{p.get('id')}' != '{pid}'")
        quizzes = p.get("quizzes", [])
        if not 1 <= len(quizzes) <= MAX_QUIZZES:
            errors.append(f"{pid}: has {len(quizzes)} quizzes (allowed 1-{MAX_QUIZZES})")
        dist = [0, 0, 0, 0]
        for zi, z in enumerate(quizzes, 1):
            qs = z.get("questions", [])
            if not z.get("topic"): errors.append(f"{pid} quiz {zi}: missing topic")
            if len(qs) != Q_PER_QUIZ: errors.append(f"{pid} quiz {zi}: {len(qs)} questions (need {Q_PER_QUIZ})")
            for qi, q in enumerate(qs, 1):
                tag = f"{pid} quiz {zi} q{qi}"
                opts = q.get("options", [])
                if not q.get("q"): errors.append(f"{tag}: empty question")
                if len(opts) != 4 or len(set(opts)) != 4: errors.append(f"{tag}: needs 4 distinct options")
                if q.get("correct") not in (0, 1, 2, 3): errors.append(f"{tag}: correct must be 0-3")
                else: dist[q["correct"]] += 1
                if not q.get("explain"): errors.append(f"{tag}: missing explanation")
        n = sum(dist); total_q += n; total_z += len(quizzes)
        skew = max(dist) / n if n else 0
        warn = "  <-- WARNING: answer key lopsided, reshuffle options" if skew > 0.4 else ""
        print(f"  {pid:28} quizzes={len(quizzes):3}  questions={n:4}  A/B/C/D={dist}{warn}")
    print(f"  TOTAL: {len(order)} policies, {total_z} quizzes, {total_q} questions")
    if errors:
        print("\nERRORS:"); [print("  -", e) for e in errors]; sys.exit(1)
    print("  OK")

if __name__ == "__main__":
    main()
