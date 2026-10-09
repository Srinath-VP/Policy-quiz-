# Policy Quiz Hub

A single-page MCQ quiz dashboard for bank staff training (STC Piravalur). Pick a **policy** from a dropdown, pick a **quiz** (numbered by topic), answer 10 multiple-choice questions, and get instant right/wrong feedback, an explanation for every question, and a score at the end.

No server, no database, no login. The whole app is one static HTML file, so it can be hosted free anywhere.

## What's in it today

| Policy | Quizzes | Questions |
|---|---|---|
| KYC / AML / CFT Policy | 8 | 80 |
| Compliance Policy | 10 | 100 |
| Inspection & Audit Policies | 9 | 90 |
| Inspection Circulars 2026 | 2 | 20 |
| Types of Customer 2026 | 10 | 100 |
| Vigilance Policy (Whistle Blower & Fraud Risk) | 10 | 100 |
| **Total** | **49** | **490** |

**Model Questions 2026** (separate tab, exam mode): 300 questions from *Model Questions for Promotion Examinations 2026-27*, in 6 sets of 50 (Q1–50 … Q251–300). Questions and options keep the paper's exact order. Answers are not shown during the test. You can change answers, jump between questions, and submit; then every answer is checked against the official answer key, and you get the score plus a full answer key (with an "only wrong / unanswered" filter). The source paper's Q113 lists "HDFC Ltd" twice (options B and C). It is kept as printed, and the answer is A.

**New Policy Quiz** (third tab, exam mode): 24 quizzes with 690 questions in total, one quiz per training PDF in `New-policy-quiz/`. There are 21 PDFs with 30 questions each and 3 PDFs (TDS/Form 121/STR-CTR, Fund Based Limits, NPA Management) with 20 each. Every question and explanation is taken from its PDF, and answers are scored on submit with a full answer key.

**Study Notes** (fourth tab): quick-revision tables built from the same PDFs. **TAT** covers turnaround times, **Committees** shows who decides what, **Grievance** gives complaint timelines and escalation, and **Important Years** lists one line per year on what came in and why. There is a search box, and every entry names its source PDF.


Each policy can grow to **100 quizzes × 10 questions**. The validator enforces that limit.

## Folder layout

```
policy-quiz-hub/
├── data/
│   ├── policies.json          # sets the dropdown order: list of policy ids
│   ├── exams.json             # exam-mode question papers (separate tab)
│   ├── new-policy.json        # New Policy Quiz collections (third tab)
│   ├── new-policy-quiz.json
│   ├── model-questions-2026.json
│   ├── kyc-aml-cft.json       # one file per policy (see schema below)
│   └── ...
├── src/template.html          # UI (HTML/CSS/JS). Data is injected at build time
├── scripts/
│   ├── validate.py            # checks every data file (run automatically by build)
│   └── build.py               # bakes data into dist/
└── dist/
    ├── index.html             # ← the deployable app (standalone page)
    └── artifact.html          # same app as a fragment, for publishing as a Claude artifact
```

## Quick start

```bash
python3 scripts/build.py        # validates data, then writes dist/index.html
# open dist/index.html in any browser (double-click works)
```

You only need Python 3.8+. There are no npm or pip dependencies.

## Data schema (one file per policy)

```json
{
  "id": "vigilance",
  "policyName": "Vigilance Policy (Whistle Blower & Fraud Risk)",
  "quizzes": [
    {
      "topic": "Whistle Blower Policy – Objective, Definition & Custodian",
      "questions": [
        {
          "q": "Question text",
          "options": ["A", "B", "C", "D"],
          "correct": 2,
          "explain": "Why C is right, citing the policy."
        }
      ]
    }
  ]
}
```

Rules (enforced by `validate.py`):

- 1–100 quizzes per policy
- exactly 10 questions per quiz
- exactly 4 distinct options per question
- `correct` is the zero-based index of the right option (0 = A … 3 = D)
- every question needs an explanation
- the validator warns if more than 40% of a policy's answers sit in one position. Shuffle the options if you see that warning.

Write plain text (use `&`, not `&amp;`). The page escapes everything when it renders.

## How to add content

**Add quizzes to an existing policy:** append new objects to that policy's `quizzes` array, then run `python3 scripts/build.py`. Quiz numbers are assigned automatically in array order.

**Add a new policy:**
1. Create `data/<new-id>.json` using the schema above (`id` must match the filename).
2. Add `"<new-id>"` to `data/policies.json` at the position you want it in the dropdown.
3. Run `python3 scripts/build.py`.

**With Claude Code:** open this folder and ask, for example: *"Read `~/Desktop/Policy-quiz/Loan Policy.pdf` and add it as a new policy with 10-question quizzes grouped by topic, following CLAUDE.md."*

## How scoring works

- Clicking an option **locks** the answer. The correct option turns green; a wrong pick turns red with a ✗. An explanation appears straight away.
- A running score ("Score 6 / 7") shows under the question.
- At the end: score out of 10, percentage, and **Passed** / **Needs review** (pass mark 70%, set by `PASS_PCT` in `src/template.html`).
- A full answer key follows: your answer, the correct answer, and the explanation for all 10 questions.
- Each quiz's best score and attempt count are saved in the browser (`localStorage`), per policy. "Reset progress for this policy" clears them.

> Scores stay in each person's own browser. Nothing is sent anywhere. If you later want a central leaderboard or a manager view, see Phase 3 below.

## Implementation plan: free hosting

The app is a single static file, so every option below is free and needs no backend.

### Option A: GitHub Pages (recommended)
1. Create a GitHub repo, e.g. `policy-quiz-hub`, and push this folder.
2. In the repo, go to **Settings → Pages → Build and deployment**. Choose **GitHub Actions**.
3. Add `.github/workflows/deploy.yml` (already included in this folder). On every push it runs `build.py` and publishes `dist/`.
4. Your URL: `https://<username>.github.io/policy-quiz-hub/`

After that, updating content is just: edit `data/*.json` → commit → push. The site redeploys itself.

### Option B: Netlify (no Git needed)
Go to **app.netlify.com/drop** and drag the `dist` folder onto the page. You get an HTTPS URL in seconds. To update, drag the new `dist` folder onto the same site.

### Option C: Cloudflare Pages / Vercel
Connect the GitHub repo. Set the **build command** to `python3 scripts/build.py` and the **output directory** to `dist`.

### Option D: Claude artifact
Publish `dist/artifact.html` as an artifact and share the link. This is what the current live version uses.

### Option E: Intranet / shared drive
Copy `dist/index.html` to any internal web server or shared folder. It works offline except for the Google Fonts, which fall back to system fonts.

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| 1 | Policy dropdown, quiz-by-topic list, 10-Q quizzes, instant validation, score, answer key | ✅ Done |
| 2 | More policies and quizzes (up to 100 per policy); optional "random 10 from whole policy" mock test; timer mode | Next |
| 3 | Central results: staff name/ID entry and results saved to a shared store (e.g. Google Sheets via Apps Script, or Supabase free tier) so trainers can see completion and scores | Optional |
| 4 | Question-bank admin: edit questions in a Google Sheet and export to `data/*.json` | Optional |

## Content note

Questions were generated from the bank's own training PDFs, and every question cites its source fact in the explanation. Before rolling out to staff, have a subject expert review each policy's questions. Circular-based content (thresholds, dates, timelines) changes over time.
