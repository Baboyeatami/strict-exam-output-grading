# Example rubric profile: EDA 1st Quarterly Examination (EMATH 311)

This is one completed, exam-specific profile from a real grading run. Use it
only when the submission is for this exam and the instructor has not supplied
a revised rubric. For any other course or exam, fill
`rubric-profile-template.md` instead; do not reuse these weights.

## Scope and maximum

The written file-output portion has two questions worth 44 points each, for a
graded maximum of 88 points:

| Question | Criterion id | Criterion | Points | Evidence expected |
|---|---|---|---|---|
| Q1 | `q1_model` | Model and physical interpretation | 4 | report + workbook |
| Q1 | `q1_visual` | Visualization and initial values/brackets | 6 | report figure / sampled data |
| Q1 | `q1_method1` | Bisection implementation | 10 | workbook formulas + history |
| Q1 | `q1_method2` | False Position implementation | 10 | workbook formulas + history |
| Q1 | `q1_verify` | Verification and convergence evidence | 8 | original-equation checks |
| Q1 | `q1_discuss` | Written discussion | 6 | report narrative |
| Q2 | `q2_model` | Model and physical interpretation | 4 | report + workbook |
| Q2 | `q2_visual` | Visualization and initial values/brackets | 6 | report figure / sampled data |
| Q2 | `q2_method1` | Newton–Raphson implementation | 10 | workbook formulas + history |
| Q2 | `q2_method2` | Secant implementation | 10 | workbook formulas + history |
| Q2 | `q2_verify` | Verification and convergence evidence | 8 | original-equation checks |
| Q2 | `q2_discuss` | Written discussion | 6 | report narrative |

Declared Q1 total: 44
Declared Q2 total: 44
Declared total: 88

The exam also has a video component (6 + 6 points). When the instructor
requests file-output-only grading, exclude video entirely and score the
written work out of 88. Do not count the excluded video points as zeros or
include them in the denominator.

## Question-specific methods

- **Question 1: tank-depth root finding.** The assigned residual models the
  tank volume as a function of depth. Review Bisection and False Position
  implementations, their bracket and stopping logic, manual checks, final
  depth and volume verification, and comparison/discussion.
- **Question 2: thermal balance.** The assigned heat-balance residual and
  derivative support Newton–Raphson; Secant uses two starting temperatures.
  Review each iteration, safeguards, final temperature and heat-loss
  verification, and comparison/discussion.

## Criterion interpretation

Use the exact exam prompt and any detailed instructor rubric if available.
The following describes the six score buckets used in the grading run:

1. **Model and physical interpretation (4):** correct assigned
   equation/residual and derivative when relevant; meaningful variables,
   units, assumptions, physical domain/feasibility, and interpretation of the
   residual or sign.
2. **Visualization and initial values/brackets (6):** useful problem graph or
   sampled data, appropriate scale and labels, zero/reference series where
   needed, justified initial guesses or a verified common bracket, and
   consistency between plotted and computed values.
3. **Each numerical method (10 per method):** correct update formula and
   spreadsheet/notebook implementation; references and retained iteration
   history; manual numerical checks; stopping logic and protections against
   invalid division, nonfinite values, domain violations, or excessive
   iterations as required by the prompt. A static list of plausible values
   does not establish a functioning formula implementation when formulas are
   required.
4. **Verification and convergence evidence (8):** substitute reported roots
   back into the original assigned equation; check residual/error and
   tolerance, iteration count, units, and requested rounding; compare the
   methods with a suitable convergence visualization when required. Reconcile
   discrepancies between report and workbook/notebook.
5. **Written discussion (6):** accurately interpret the result, compare
   methods using submitted evidence, discuss limitations/failure modes where
   required, and justify a method choice. Unsupported claims lose credit only
   under the relevant criterion.

These descriptions do not create additional points. Divide each bucket into
subcriteria only when the prompt/rubric supports that division; make
subcriterion points sum exactly to the bucket maximum.

## Strict evidence checks from this exam

- Check the report and computational file together. A correct written answer
  does not prove a workbook formula works; a working iteration table does not
  fix an unreconciled report claim.
- Independently substitute final values into the original equation. Do not
  accept a claimed PASS if the residual or units contradict it.
- Verify stopping logic against the required tolerance and whether it uses the
  correct current/next residual or bracket bound.
- Check that chart axes, series, sampling interval, and ranges reflect the
  assigned problem and actual computation.
- Distinguish a valid algorithm with a presentation omission from a broken
  formula or invalid result; award criterion-specific partial credit.
- Search related nested student folders before marking a submission missing.
  If identity or group membership remains uncertain, mark pending and request
  the missing association rather than borrowing another student's result.

## Gate

- Arithmetic verified with: `python3 scripts/check_gradebook.py profile <this file>`
- Result: pass (12 criteria rows; 44 + 44 = 88).
