#!/usr/bin/env python3
"""Validate every policy and exam file in data/ before building.

Policies (data/policies.json): <=100 quizzes, exactly 10 questions per quiz, 4 distinct options,
one correct index (0-3), non-empty explanation. Also warns if the answer key is lopsided.
Exams (data/exams.json, data/new-policy.json): same checks, but the per-quiz count comes from
`questionsPerQuiz` (or, when absent, any 10-50 per quiz), options keep the source paper's order
(no lopsided warning) and duplicate options only warn, because they are copied verbatim from the paper.
Exit code 1 on any error.
"""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAX_QUIZZES, Q_PER_QUIZ = 100, 10

def check(pid, exam, errors, warnings):
    path = ROOT / f"data/{pid}.json"
    if not path.exists():
        errors.append(f"{pid}: listed but data/{pid}.json is missing"); return 0, 0
    p = json.loads(path.read_text(encoding="utf-8"))
    if p.get("id") != pid: errors.append(f"{path.name}: id '{p.get('id')}' != '{pid}'")
    per_quiz = p.get("questionsPerQuiz") if exam else Q_PER_QUIZ
    quizzes = p.get("quizzes", [])
    if not 1 <= len(quizzes) <= MAX_QUIZZES:
        errors.append(f"{pid}: has {len(quizzes)} quizzes (allowed 1-{MAX_QUIZZES})")
    dist = [0, 0, 0, 0]
    for zi, z in enumerate(quizzes, 1):
        qs = z.get("questions", [])
        if not z.get("topic"): errors.append(f"{pid} quiz {zi}: missing topic")
        if per_quiz is None:
            if not 10 <= len(qs) <= 50: errors.append(f"{pid} quiz {zi}: {len(qs)} questions (need 10-50)")
        elif len(qs) != per_quiz: errors.append(f"{pid} quiz {zi}: {len(qs)} questions (need {per_quiz})")
        for qi, q in enumerate(qs, 1):
            tag = f"{pid} quiz {zi} q{q.get('n', qi)}"
            opts = q.get("options", [])
            if not q.get("q"): errors.append(f"{tag}: empty question")
            if len(opts) != 4: errors.append(f"{tag}: needs 4 options")
            elif len(set(opts)) != 4:
                (warnings if exam else errors).append(f"{tag}: options are not distinct")
            if q.get("correct") not in (0, 1, 2, 3): errors.append(f"{tag}: correct must be 0-3")
            else: dist[q["correct"]] += 1
            if not q.get("explain"): errors.append(f"{tag}: missing explanation")
    n = sum(dist)
    skew = max(dist) / n if n else 0
    warn = "  <-- WARNING: answer key lopsided, reshuffle options" if skew > 0.4 and not exam else ""
    print(f"  {pid:28} quizzes={len(quizzes):3}  questions={n:4}  A/B/C/D={dist}{warn}")
    return len(quizzes), n

def main():
    errors, warnings, total_q, total_z = [], [], 0, 0
    lists = [("policies.json", False), ("exams.json", True), ("new-policy.json", True)]
    count = 0
    for fname, exam in lists:
        f = ROOT / "data" / fname
        if not f.exists(): continue
        order = json.loads(f.read_text())
        print(f"  [{fname}]")
        for pid in order:
            z, q = check(pid, exam, errors, warnings); total_z += z; total_q += q; count += 1
    print(f"  TOTAL: {count} sets, {total_z} quizzes, {total_q} questions")
    if warnings:
        print("\nWARNINGS:"); [print("  -", w) for w in warnings]
    if errors:
        print("\nERRORS:"); [print("  -", e) for e in errors]; sys.exit(1)
    print("  OK")

if __name__ == "__main__":
    main()
