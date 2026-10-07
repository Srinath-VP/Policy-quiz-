# CLAUDE.md: Policy Quiz Hub

A static, single-page MCQ quiz app for bank policy training. It has no backend and no npm. Python 3 builds it.

## Commands
- `python3 scripts/validate.py`: check all question data (run it after any data edit)
- `python3 scripts/build.py`: validate, then write `dist/index.html` (standalone) and `dist/artifact.html` (fragment)

Always run `build.py` after changing `data/` or `src/`. Never hand-edit `dist/`.

## Architecture
- `data/policies.json`: an ordered list of policy ids. This order is the dropdown order.
- `data/<id>.json`: `{ id, policyName, quizzes: [{ topic, questions: [{ q, options[4], correct(0-3), explain }] }] }`
- `data/exams.json`: ordered list of exam-mode papers, shown under the "Model Questions 2026" tab. An exam file uses the same schema plus `"mode": "exam"`, `"questionsPerQuiz"` (e.g. 50), and an optional `n` (the paper's question number) on each question. Exam questions are verbatim from the paper: never shuffle their options, because `correct` must match the official answer key.
- `data/new-policy.json`: ordered list for the "New Policy Quiz" tab. It uses the same exam-mode schema with `"unit": "Quiz"`, and question counts may differ per quiz (10-50). Each quiz has a `source` naming its PDF.
- `src/template.html`: all UI, CSS, and JS in one file. `build.py` replaces the markers `/*__POLICIES__*/[]`, `/*__EXAMS__*/[]` and `/*__NEWPOLICY__*/[]` with the data arrays. Keep each marker exactly once.
- Progress is stored in `localStorage` under the key `policy_quiz_hub_v1`, shaped as `{ [policyId]: { [quizIndex]: {best, bestScore, last, attempts} } }`. If you change the shape, bump the key.

## Rules for generating questions from a policy PDF
1. Read the **whole** PDF, 20 pages per read, before writing anything.
2. Group content by topic. Each topic becomes one quiz of **exactly 10** questions. A policy can have at most 100 quizzes. Produce fewer quizzes rather than padding with weak ones.
3. Ground every question, option, and explanation in the PDF text. Never invent numbers, dates, or rules.
4. Give 4 distinct options with one correct answer. Wrong options must be plausible, e.g. another real threshold or role from the same document.
5. The explanation cites the specific fact that makes the answer right.
6. **Balance the answer key**: spread `correct` across positions 0-3 (shuffle the options). The validator warns when more than 40% of answers sit in one position.
7. Write plain text. Do not HTML-escape (the UI escapes at render).
8. Avoid position-dependent options such as "All of the above".
9. Give the policy a kebab-case `id` that matches its filename, and add it to `data/policies.json`.

## UI conventions
- Theme tokens live on `:root`, with dark mode handled by the `prefers-color-scheme` block and the `[data-theme="dark"]` block. Style through the tokens and never hard-code colors.
- Use no `alert` / `confirm` / `prompt` (artifact hosts block them). Use two-click confirms instead.
- Any user or data text inserted with `innerHTML` must go through `esc()`.
- The page must work at 400px width.
