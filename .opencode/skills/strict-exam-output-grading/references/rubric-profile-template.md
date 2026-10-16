# Rubric profile (canonical format)

This is the canonical profile format. In normal use the skill builds it
automatically from the instructor's rubric during intake; fill it by hand only
to override the auto-built profile or when working in a harness without the
scripts. The profile is the source of truth for the run. Keep the table format
exactly as shown so `scripts/check_gradebook.py profile <this file>` can
verify the arithmetic.

## Exam identity

- Exam title: `<title>`
- Course/section: `<course>`
- Questions source (file + path/link): `<source>`
- Rubric source (file + path/link): `<source>`
- Results folder: `<path>`
- Roster supplied: `yes/no`

## Scope

- Declared total: `<points>`
- Declared Q1 total: `<points>`
- Declared Q2 total: `<points>`
  (Add one `Declared Q<N> total:` line per question. These numbers come from
  the instructor's rubric, not from the table below.)
- Included evidence types: `<e.g. workbook, report, notebook, pdf>`
- Excluded evidence types (never opened or scored): `<e.g. video>`
- Denominator rule: excluded points are removed from the maximum, never scored
  as zero. Adjusted maximum: `<points>`
- Rounding / percent policy: `percent = earned / adjusted maximum x 100`,
  no letter grade or pass cutoff unless the instructor states one.
- Penalty policy: none unless the instructor states one in writing.

## Criteria

| Question | Criterion id | Criterion | Points | Evidence expected |
|---|---|---|---|---|
| Q1 | `q1_a` | `<criterion>` | `<points>` | `<file/sheet/section/figure>` |
| Q1 | `q1_b` | `<criterion>` | `<points>` | `<file/sheet/section/figure>` |
| Q2 | `q2_a` | `<criterion>` | `<points>` | `<file/sheet/section/figure>` |
| Q2 | `q2_b` | `<criterion>` | `<points>` | `<file/sheet/section/figure>` |

Rules:

- One row per scored criterion. Criterion ids are unique, lowercase, no spaces.
- Points per question must sum to that question's declared total; all questions
  must sum to the declared overall total.
- Subcriteria (only when the instructor's rubric defines them) must sum exactly
  to the parent criterion's points; express them as separate rows with ids like
  `q1_a_1` and state the parent in the criterion text.

## Scoring conventions

- Partial credit: describe how partial credit is awarded where the rubric
  supports it; otherwise state "all-or-nothing per criterion".
- Evidence standard: state what counts as proof (for example, "iteration
  values with a final root; prose claims alone earn no points").
- No double deduction: one defect must not be penalized under two criteria.
- Pending rule: uncertain identity or inaccessible files leave the affected
  student `pending` with a reason; never assign zero for absence alone.
- Attribution rule: match order and duplicate handling (count duplicates once).

## Gate

- Arithmetic verified with: `python3 scripts/check_gradebook.py profile <this file>`
- Result: `pass/fail` — grading must not start on `fail` without a recorded
  instructor override.
