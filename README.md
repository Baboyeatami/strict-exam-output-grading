# Strict Exam Output Grading (OpenCode skill)

An OpenCode skill for grading student exam submissions strictly against an
instructor-supplied rubric, using the files in a results folder as the only
evidence. It works for **any exam** — you just provide the exam questions and
rubric, then the folder of student outputs.

The skill builds the scoring profile from the instructor's rubric
automatically (in the canonical format described below), validates the
arithmetic, and only then grades. Weights from one exam are never reused for
another; the EDA/EMATH 311 profile in `references/` is only a completed
example.

---

## How it works

1. **You provide the questions + rubric** (files or pasted text; the rubric
   may be a separate file or embedded in the questions document, in docx,
   xlsx, pdf, md, or text form).
2. **The skill builds and validates the scoring profile**: it extracts the
   rubric, converts it into the canonical profile format, runs the arithmetic
   gate (`check_gradebook.py profile`), and reports a compact summary —
   questions, criteria, maximum, excluded points, gate result.
   - Explicit rubric + passing gate → grading proceeds automatically.
   - Missing points, unmapped criteria, unclear exclusions, or failing
     arithmetic → the skill stops and asks instead of guessing.
3. **You provide the folder of student outputs** (nested folders are fine).
4. **The skill grades**: inventory and attribution, evidence extraction,
   independent verification, criterion scoring, reconciliation, gradebook
   and feedback — all written to `./grading-run/` (overridable), never into
   your results folder.

---

## Contents

```
.opencode/
  command/grade-exam.md       one-line slash command for the whole flow
  skills/strict-exam-output-grading/
    SKILL.md                  intake, readiness gate, workflow, scoring rules
    references/
      rubric-profile-template.md      canonical profile format (auto-built)
      eda-numerical-methods-profile.md  completed example (EMATH 311)
      provider-adapter.md             harness mapping incl. OpenCode + JSON shapes
    scripts/
      extract_text.py         stdlib text dump: docx, xlsx, pdf, ipynb, text
      check_gradebook.py      profile arithmetic + gradebook/expected validation
validation/
  fixture-exam/               synthetic exam, raw + canonical rubric, roster
  expected_scores.json        fixture ground truth
  expected_gradebook.json     canonical gradebook shape
  make_fixtures.py            regenerates the synthetic results folder
  run_validation.py           scripted validation suite
  checklist.md                scripted + agent-run checklist
```

---

## Install

**Option A — this repo.** The skill and `/grade-exam` command are already
discoverable by OpenCode when you run OpenCode from this repository. Quit and
restart OpenCode first (skills and commands load at startup; they are not
hot-reloaded).

**Option B — one project.** Copy the skill folder (and the command, if
wanted):

```bash
mkdir -p /path/to/project/.opencode/skills /path/to/project/.opencode/command
cp -R .opencode/skills/strict-exam-output-grading /path/to/project/.opencode/skills/
cp .opencode/command/grade-exam.md /path/to/project/.opencode/command/
```

Restart OpenCode in that project. No `opencode.json` change is needed.

**Option C — all projects (global).** Install the skill and command globally:

```bash
mkdir -p ~/.config/opencode/skills ~/.config/opencode/command
cp -R .opencode/skills/strict-exam-output-grading ~/.config/opencode/skills/
cp .opencode/command/grade-exam.md ~/.config/opencode/command/
```

Restart OpenCode. The skill and `/grade-exam` then work from any project;
the command locates the skill in the project or global directory.

**Other harnesses (Claude Code, Codex, etc.).** Use
`strict-exam-output-grading.zip` or the folder contents as skill/context
files. The grading rules are model-agnostic; only the tool mapping changes.
See `references/provider-adapter.md`.

---

## Quick start

### 1. Call the skill

In OpenCode, ask naturally:

> Grade the exams in `exams/emath311/results` using the questions in
> `exams/emath311/questions.pdf` and the rubric in
> `exams/emath311/rubric.xlsx`. Exclude the video demos.

Or use the one-line command with the three inputs:

```
/grade-exam exams/emath311/questions.pdf exams/emath311/rubric.xlsx exams/emath311/results
```

Partial arguments are fine — the skill requests whatever is missing, in
order. A typical interactive session:

```
You:      grade my EDA exam
Skill:    Please share the exam questions and rubric (files or text).
You:      [questions.pdf] [rubric.xlsx] — video demos are excluded
Skill:    Profile built from the rubric: 2 questions, 12 criteria, max 88
          (video 12 pts excluded, not zeroed). Arithmetic gate passed.
          Now share the folder with the student outputs.
You:      exams/emath311/results
Skill:    [grades; writes grading-run/]
```

The skill pauses only for genuine ambiguity in the rubric — missing points,
a criterion that cannot be mapped to a question or artifact, unclear
exclusion handling, or failing arithmetic.

### 2. Review the outputs

Everything lands in `./grading-run/` (override with the destination you
specify):

```
grading-run/
  profile.md        built rubric profile (audit trail of criteria and points)
  gradebook.xlsx    one row per student: status, per-criterion scores,
                    totals, percent, notes (CSV + Markdown fallback)
  gradebook.json    internal machine-readable format (validator-compatible)
  feedback.md       per-student feedback with concrete evidence
  manifest.md       inputs, hashes, assumptions, overrides, pending items
```

- **Pending** means the skill could not resolve something (missing file,
  ambiguous identity, only-excluded-media submission). Pending is never a
  zero. Resolve it and ask for a re-check:

  > Elle Delta submitted `Delta_final.docx` late — it's now in results/.
  > Re-check Elle Delta and update the gradebook.

- **Feedback** is student-specific and evidence-linked; length and format
  follow your instructions (e.g. "two paragraphs per student").

### 3. Validate the gradebook (optional)

```bash
python3 .opencode/skills/strict-exam-output-grading/scripts/check_gradebook.py \
  gradebook grading-run/gradebook.json
```

Checks: exam maximum equals the sum of criterion maxima, scored students
have every criterion, scores are within bounds, totals equal the sum of
scores, percents match the denominator, and pending students carry no
numeric values. Add `--expected expected_scores.json` to compare against a
known ground truth.

---

## What happens during a run

1. **Intake** — questions + rubric extracted; canonical profile built from
   the rubric's own criteria and points; arithmetic gate validated.
2. **Inventory and attribution** — the results folder is traversed
   recursively; every file is recorded (name, path, type, size, hash);
   files are matched to the roster in order (exact name → filename patterns
   → group evidence inside the file → instructor confirmation); duplicates
   count once; anything uncertain stays `pending`.
3. **Evidence extraction** — submissions are read with
   `scripts/extract_text.py`, keeping provenance for every observation
   (file + sheet/cell/page/table/figure). Excluded media is never opened.
4. **Independent verification** — rubric-critical numbers are recomputed
   from the exam's own equations and compared with the submitted report and
   workbook; discrepancies are recorded with both values and locations.
5. **Criterion scoring** — each rubric row is scored; deductions cite a
   criterion and an evidence location; no double penalties; partial credit
   where the rubric supports it.
6. **Reconciliation** — per-question and overall sums re-checked with zero
   tolerance; the denominator uses only included criteria; pending students
   stay out of the aggregates.
7. **Deliverables** — gradebook + feedback + profile + run manifest written,
   read back, and verified.

---

## Advanced: overriding the profile

Normally you never touch the profile — the skill builds it. Override it when
you want to pre-approve the criteria mapping, correct a gate failure, or use
a harness without the scripts:

1. Copy
   `.opencode/skills/strict-exam-output-grading/references/rubric-profile-template.md`
   to your exam folder (e.g. `exam-2026/profile.md`).
2. Fill it from the instructor's rubric. Required format:

   ```
   | Question | Criterion id | Criterion | Points | Evidence expected |
   |---|---|---|---|---|
   | Q1 | q1_a | Bisection: iteration values and final root | 5 | workbook or report table |
   ```

   plus declared totals on their own lines:

   ```
   - Declared total: 20
   - Declared Q1 total: 10
   - Declared Q2 total: 10
   ```

   and the exclusion rule ("video demo excluded — removed from the
   maximum, never scored as zero").
3. Verify before grading:

   ```bash
   python3 .opencode/skills/strict-exam-output-grading/scripts/check_gradebook.py \
     profile exam-2026/profile.md
   ```

   `PASS` means every question's criteria sum to its declared total and the
   overall sum matches. `FAIL` means the rubric or the profile is
   inconsistent — fix it or ask the instructor before grading.

Then point the skill at your profile, or simply include it with the other
inputs. Rules of thumb: criterion ids are unique, lowercase, no spaces;
subcriteria (only when the instructor's rubric defines them) must sum
exactly to the parent's points; one profile per exam; keep the table format
exactly as shown so the script can parse it.

---

## Scripts

**`extract_text.py`** — dependency-free text extraction (Python stdlib
only):

```bash
python3 .opencode/skills/strict-exam-output-grading/scripts/extract_text.py \
  exam-2026/results/JaneDoe_Workbook.xlsx
```

Supported: `.docx`, `.xlsx` (cell values as `A1=value` lines per sheet),
`.pdf` (text PDFs; no OCR for scans), `.ipynb`, and plain-text formats
(`.txt .md .csv .json .py .html .xml .tex .log`). Images, video, and archives
are reported as not text-extractable.

**`check_gradebook.py`** — two modes:

```bash
# 1. Rubric profile arithmetic (run during intake / before grading)
python3 .../check_gradebook.py profile exam-2026/profile.md

# 2. Gradebook validation, optionally against expected ground truth
python3 .../check_gradebook.py gradebook grading-run/gradebook.json \
  [--expected exam-2026/expected_scores.json]
```

Exit code `0` = all checks passed; `1` = failures printed line by line.

---

## Gradebook JSON shape

The skill's internal gradebook format (the adapter reference has the full
description):

```json
{
  "exam": {"title": "...", "max": 20, "excluded": ["video"]},
  "criteria": [{"id": "q1_a", "question": "Q1", "max": 5}],
  "students": [
    {"name": "...", "status": "scored", "scores": {"q1_a": 5},
     "total": 20, "percent": 100.0, "notes": "evidence..."},
    {"name": "...", "status": "pending", "scores": {},
     "total": null, "percent": null, "notes": "reason..."}
  ]
}
```

Scored students must have every criterion scored; pending students have no
numeric totals; the exam maximum equals the sum of criterion maxima. Convert
to XLSX/CSV for the instructor as the final deliverable.

---

## Guarantees and boundaries

- Excluded media (video, etc.) is never opened or scored and is removed from
  the denominator — not counted as zeros.
- Missing, uncertain, or unattributable submissions stay pending (never
  zero, never silently dropped).
- The skill never invents weights, criteria, totals, penalties, letter
  grades, or pass cutoffs — only what the instructor's rubric states.
- Every deduction cites a criterion and an evidence location; no double
  deductions; partial credit where the rubric supports it.
- Nothing is written into the results folder, and every write is read back
  and verified.
- All fixtures in this repo are synthetic; keep real student data out of the
  repository.

---

## Development / validation

Regenerate the synthetic fixture and run the full scripted suite:

```bash
python3 validation/make_fixtures.py      # rebuild validation/fixture-exam/results/
python3 validation/run_validation.py     # all checks must print PASS
```

The suite covers: profile arithmetic (good passes, broken fails), the EDA
example profile (44 + 44 = 88), canonical gradebook vs expected scores,
corrupted gradebook rejection, extraction of planted values in
docx/xlsx/pdf, raw-rubric extraction for intake, and untouched excluded
media. `validation/checklist.md` lists the additional behaviors to verify in
an agent grading run.
