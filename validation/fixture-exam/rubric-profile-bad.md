# Rubric profile — EMATH 100 Make-Up Quiz (synthetic fixture, BROKEN ON PURPOSE)

Negative test fixture: `q2_secant` is inflated from 5 to 6 so the Q2 sum and
the overall sum no longer match the declared totals. The readiness gate must
fail and grading must not start.

## Exam identity

- Exam title: EMATH 100 Make-Up Quiz (synthetic fixture)
- Course/section: EMATH 100 / fixture
- Questions source (file + path/link): validation/fixture-exam/exam-questions.md
- Rubric source (file + path/link): validation/fixture-exam/rubric-profile-bad.md
- Results folder: validation/fixture-exam/results
- Roster supplied: yes

## Scope

- Declared total: 20
- Declared Q1 total: 10
- Declared Q2 total: 10
- Included evidence types: docx reports, xlsx workbooks, pdf reports
- Excluded evidence types (never opened or scored): video (.mp4)
- Denominator rule: excluded video demo removed from the maximum. Adjusted maximum: 20
- Rounding / percent policy: percent = earned / 20 x 100
- Penalty policy: none

## Criteria

| Question | Criterion id | Criterion | Points | Evidence expected |
|---|---|---|---|---|
| Q1 | `q1_bisect` | Bisection: iteration values and final root | 5 | workbook sheet or report table |
| Q1 | `q1_newton` | Newton-Raphson: iteration values and final root | 5 | workbook sheet or report table |
| Q2 | `q2_secant` | Secant: iteration values and final root | 6 | workbook sheet or report table |
| Q2 | `q2_falsepos` | False Position: values and final root | 5 | workbook sheet or report table |

## Scoring conventions

- Partial credit: none in this fixture (all-or-nothing per criterion).
- Evidence standard: iteration values in a workbook sheet or report table.
- Pending rule: uncertain identity leaves the student pending; never zero.
- Attribution rule: duplicates count once.

## Gate

- Arithmetic verified with: `python3 .opencode/skills/strict-exam-output-grading/scripts/check_gradebook.py profile validation/fixture-exam/rubric-profile-bad.md`
- Result: fail (expected; this file is the negative test)
