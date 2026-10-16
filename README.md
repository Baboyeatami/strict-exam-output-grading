# Strict Exam Output Grading (OpenCode skill)

An OpenCode skill for grading student exam submissions strictly against an
instructor-supplied rubric, using the files in a results folder as the only
evidence. It works for **any exam** as long as you provide:

1. the exam questions/instructions,
2. the rubric with criteria and points, and
3. a folder containing the student results (nested folders are fine).

The skill defines the grading **process**; each exam's weights and criteria
come from a rubric profile you fill for that exam. The EDA/EMATH 311 profile
in `references/` is one completed example — its weights are never applied to
another exam.

---

## Contents

```
.opencode/skills/strict-exam-output-grading/
  SKILL.md                    workflow: inputs, readiness gate, scoring, deliverables
  references/
    rubric-profile-template.md        fill one per exam (required before grading)
    eda-numerical-methods-profile.md  completed example (EMATH 311)
    provider-adapter.md               harness mapping incl. OpenCode + JSON shapes
  scripts/
    extract_text.py           stdlib text dump: docx, xlsx, pdf, ipynb, text
    check_gradebook.py        profile arithmetic + gradebook/expected validation
validation/
  fixture-exam/               synthetic exam, good + broken rubric, roster
  expected_scores.json        fixture ground truth
  expected_gradebook.json     canonical gradebook shape
  make_fixtures.py            regenerates the synthetic results folder
  run_validation.py           scripted validation suite
  checklist.md                scripted + agent-run checklist
```

---

## Install

**Option A — this repo.** The skill is already discoverable by OpenCode when
you run OpenCode from this repository. Quit and restart OpenCode first
(skills load at startup; they are not hot-reloaded), then ask it to grade an
exam.

**Option B — one project.** Copy the skill folder:

```bash
mkdir -p /path/to/project/.opencode/skills
cp -R .opencode/skills/strict-exam-output-grading /path/to/project/.opencode/skills/
```

Restart OpenCode in that project. No `opencode.json` change is needed.

**Option C — all projects (global).** Copy the folder to the global skills
directory instead:

```bash
mkdir -p ~/.config/opencode/skills
cp -R .opencode/skills/strict-exam-output-grading ~/.config/opencode/skills/
```

Restart OpenCode.

**Other harnesses (Claude Code, Codex, etc.).** Use `strict-exam-output-grading.zip`
or the folder contents as skill/context files. The grading rules are
model-agnostic; only the tool mapping changes. See
`references/provider-adapter.md`.

---

## Quick start

### 1. Prepare the three inputs

You need a questions source, a rubric, and a results folder. A typical exam
folder looks like this:

```
exam-2026/
  questions.pdf          # or .md/.docx — the exam prompt/instructions
  rubric.xlsx            # or .md/.docx/.pdf — criteria and points
  roster.csv             # optional but recommended: name,section
  results/               # the results folder
    JaneDoe_Q1_Report.docx
    JaneDoe_Workbook.xlsx
    Group3/
      report.pdf
      workbook.xlsx
```

The results folder may be flat, nested, contain group submissions, or hold
duplicate versions — the skill handles all of these, but it needs to be able
to read the files (local path, or a path mounted/synced to disk).

### 2. Fill one rubric profile

The profile is the single source of truth for the run. Copy
`.opencode/skills/strict-exam-output-grading/references/rubric-profile-template.md`
to your exam folder (e.g. `exam-2026/profile.md`) and fill it from the
instructor's rubric. Minimum requirements:

- One row per scored criterion in this exact table format:

  ```
  | Question | Criterion id | Criterion | Points | Evidence expected |
  |---|---|---|---|---|
  | Q1 | q1_a | Bisection: iteration values and final root | 5 | workbook or report table |
  ```

- Declared totals on their own lines, matching the rubric:

  ```
  - Declared total: 20
  - Declared Q1 total: 10
  - Declared Q2 total: 10
  ```

- Excluded evidence types and the denominator rule, for example:
  "video demo (5 points) excluded — removed from the maximum, never scored as
  zero."

You can ask OpenCode to draft the profile from your rubric files; **verify
the declared totals yourself** — they must come from the instructor's rubric,
not from the criteria table.

Check the arithmetic before grading:

```bash
python3 .opencode/skills/strict-exam-output-grading/scripts/check_gradebook.py \
  profile exam-2026/profile.md
```

`PASS` means every question's criteria sum to its declared total and the
overall sum matches. `FAIL` means the rubric or the profile is inconsistent —
fix it or ask the instructor before grading.

### 3. Ask OpenCode to grade

Example prompt:

> Grade the exams in `~/exams/emath311/results` using the questions in
> `~/exams/emath311/questions.pdf` and the rubric profile in
> `~/exams/emath311/profile.md`. Exclude the video demos. Write the gradebook
> and feedback to `~/exams/emath311/out/`.

What the skill does, in order:

1. **Readiness gate** — checks the profile arithmetic, that every criterion
   maps to a question and an observable artifact, that the results folder is
   readable, and that excluded-point handling is stated. Stops and reports
   if something is wrong.
2. **Inventory and attribution** — walks the folder recursively, records
   every file (name, path, type, size, hash), matches files to the roster in
   order (exact name → filename patterns → group evidence inside the file →
   instructor confirmation), counts duplicates once, and keeps anything
   uncertain as `pending`.
3. **Evidence extraction** — reads each submission (docx, xlsx, pdf,
   notebooks, images when permitted) with `scripts/extract_text.py`, keeping
   provenance for every observation (file + sheet/cell/page/table/figure).
   Excluded media is never opened.
4. **Independent verification** — recomputes rubric-critical numbers from
   the exam's own equations and compares them with the submitted report and
   workbook; discrepancies are recorded with both values and locations.
5. **Criterion scoring** — scores each rubric row, awards partial credit
   where supported, cites evidence for every deduction, and never
   double-penalizes one defect.
6. **Reconciliation** — re-sums per question and overall, uses only included
   criteria in the denominator, and keeps pending students out of the
   aggregates.
7. **Deliverables** — XLSX gradebook (with a numerical-checks sheet when
   relevant) plus per-student feedback with concrete evidence; CSV +
   Markdown if no spreadsheet writer is available. Any write is read back
   and verified. A run manifest records inputs, hashes, assumptions,
   overrides, and pending items.

### 4. Review the outputs

- **Gradebook** — one row per student: status (`scored`/`pending`), one
  column per criterion, totals, percent, feedback reference, notes.
- **Feedback** — student-specific, evidence-linked; length/format follows
  your instructions (e.g. "two paragraphs per student").
- **Pending list** — students or submissions the skill could not resolve
  (missing file, ambiguous identity, excluded-only submission). Pending is
  never a zero; resolve the question and ask for a re-check:

> Elle Delta submitted `Delta_final.docx` late — it's now in results/.
> Re-check Elle Delta and update the gradebook.

### 5. Validate the gradebook (optional)

If the run produced `gradebook.json` (the skill's internal format), you can
verify it independently:

```bash
python3 .opencode/skills/strict-exam-output-grading/scripts/check_gradebook.py \
  gradebook exam-2026/out/gradebook.json
```

Checks: exam maximum equals the sum of criterion maxima, scored students
have every criterion, scores are within bounds, totals equal the sum of
scores, percents match the denominator, and pending students carry no
numeric values. Add `--expected expected_scores.json` to compare against a
known ground truth (as the validation suite does).

---

## Working with the rubric profile

The profile is the only exam-specific file. Everything else (workflow,
evidence standard, pending rules) is reusable. Fields explained:

| Field | What it does |
|---|---|
| Questions/rubric source | Pointers so the run is auditable |
| Results folder | The folder to traverse recursively |
| Declared totals | Rubric maxima per question and overall — verified by the script |
| Included/excluded evidence types | What may be opened and scored |
| Denominator rule | How excluded points are handled (removed from max, never zeros) |
| Rounding / percent policy | e.g. `percent = earned / adjusted max x 100` |
| Criteria table | One row per criterion: question, unique id, points, evidence expected |
| Scoring conventions | Partial credit, evidence standard, no-double-deduction, pending, attribution |
| Gate | The verification command and its result |

Rules of thumb:

- Criterion ids are unique, lowercase, no spaces (`q1_bisect`).
- Subcriteria only when the instructor's rubric defines them; they must sum
  exactly to the parent criterion's points.
- Keep the table format exactly — `check_gradebook.py profile` parses it.
- One profile per exam. Never reuse another exam's weights.

---

## Scripts

**`extract_text.py`** — dependency-free text extraction (uses only Python
stdlib). Use it manually to inspect a submission the way the skill does:

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
# 1. Rubric profile arithmetic (run before grading)
python3 .../check_gradebook.py profile exam-2026/profile.md

# 2. Gradebook validation, optionally against expected ground truth
python3 .../check_gradebook.py gradebook exam-2026/out/gradebook.json \
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
- Every deduction cites a criterion and an evidence location; no double
  deductions; partial credit where the rubric supports it.
- Nothing is written outside the requested deliverables, and every write is
  read back and verified.
- No letter grades, pass cutoffs, or penalties are invented — only what the
  instructor's rubric states.
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
docx/xlsx/pdf, and untouched excluded media. `validation/checklist.md` lists
the additional behaviors to verify in an agent grading run.
