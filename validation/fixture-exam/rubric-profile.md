# Rubric profile — EMATH 100 Make-Up Quiz (synthetic fixture)

## Exam identity

- Exam title: EMATH 100 Make-Up Quiz (synthetic fixture)
- Course/section: EMATH 100 / fixture
- Questions source (file + path/link): validation/fixture-exam/exam-questions.md
- Rubric source (file + path/link): validation/fixture-exam/rubric-profile.md (fixture stand-in for the instructor rubric)
- Results folder: validation/fixture-exam/results
- Roster supplied: yes (validation/fixture-exam/roster.csv)

## Scope

- Declared total: 20
- Declared Q1 total: 10
- Declared Q2 total: 10
- Included evidence types: docx reports, xlsx workbooks, pdf reports
- Excluded evidence types (never opened or scored): video (.mp4)
- Denominator rule: excluded video demo (5 points) is removed from the maximum, never scored as zero. Adjusted maximum: 20
- Rounding / percent policy: percent = earned / 20 x 100; no letter grade or cutoff
- Penalty policy: none

## Criteria

| Question | Criterion id | Criterion | Points | Evidence expected |
|---|---|---|---|---|
| Q1 | `q1_bisect` | Bisection for f(x)=x^3-x-2 on [1,2], tolerance 0.05: iteration values and final root | 5 | workbook sheet or report table |
| Q1 | `q1_newton` | Newton-Raphson from x0=1.5: iteration values and final root | 5 | workbook sheet or report table |
| Q2 | `q2_secant` | Secant with x0=2, x1=3: iteration values and final root | 5 | workbook sheet or report table |
| Q2 | `q2_falsepos` | False Position on [2,3], three iterations: values and final root | 5 | workbook sheet or report table |

## Scoring conventions

- Partial credit: in this fixture each criterion is all-or-nothing. Full
  points require iteration values with a final root within 0.01 of the true
  root (Q1 approximately 1.5214; Q2 approximately 2.0946). No values earns 0.
- Evidence standard: iteration values in a workbook sheet or report table.
  Prose claims without values earn no points.
- No double deduction: one defect is penalized under one criterion only.
- Pending rule: uncertain identity or inaccessible files leave the student
  pending with a reason; never zero.
- Attribution rule: match by name in filename, then roster; duplicates count
  once.

## Gate

- Arithmetic verified with: `python3 .opencode/skills/strict-exam-output-grading/scripts/check_gradebook.py profile validation/fixture-exam/rubric-profile.md`
- Result: pass
