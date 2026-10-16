---
name: strict-exam-output-grading
description: Grade or check any exam from instructor-supplied exam questions and rubric plus a results folder of student outputs (docx, xlsx, pdf, notebooks, images). Use when asked to grade, score, check, or audit exam outputs, build a gradebook, or prepare per-student feedback. The skill derives and validates the scoring profile from the supplied rubric automatically, then handles partial credit, pending/ambiguous submissions, excluded media such as videos, and independent numerical verification.
---

# Strict exam output grading

Grade any exam from two steps: (1) the exam questions and the instructor's
rubric, then (2) the folder of student results. The skill builds a rubric
profile from the instructor's rubric for this exam, validates it, and grades
once the gate passes. Weights from another exam (including the EDA example
profile) must never be reused.

## Intake

Obtain inputs in this order; skip ahead if some are already provided and never
block on optional items.

1. **Questions and rubric.** Accept files or pasted text; the rubric may be a
   separate file or embedded in the questions document, in any readable
   format (docx, xlsx, pdf, md, text). Then:
   - Extract the rubric with the harness tools
     (`scripts/extract_text.py` in OpenCode).
   - Draft the canonical profile (`references/rubric-profile-template.md`)
     from the instructor's rubric: one row per criterion with points and
     evidence expected, declared totals copied from the rubric, excluded
     evidence types, and the denominator rule. Do not invent weights,
     criteria, penalties, or totals.
   - Validate: `scripts/check_gradebook.py profile <profile>`. Every
     question's criteria must sum to its declared total, and the sums must
     match the exam total.
   - If the rubric is explicit and the gate passes, continue automatically.
     If points are missing, a criterion cannot be mapped to a question or
     artifact, excluded-point handling is unclear, or arithmetic fails, stop
     and ask the instructor — never guess.
2. **Results folder.** If not already provided, ask for the folder, then run
   the workflow below.

Save the built profile to the output directory (`grading-run/profile.md` by
default) and include it in the run manifest so the run is auditable.

## Inputs

Required: exam questions, rubric, results folder (local or otherwise
accessible; nested subfolders are fine).

Optional: roster, excluded evidence types, group-work rules, deliverable
format, output destination (default `./grading-run/`), or a pre-filled profile
to override the auto-built one.

Ask only when a required input is missing or the gate fails. Never write into
the results folder.

## Readiness gate

Confirm on the built profile before grading:

- Every question has criteria with points; points sum per question and overall.
- Every criterion maps to a question and to an observable artifact (file,
  sheet, section, figure).
- Excluded evidence types are recorded; criteria that can only be met through
  excluded evidence are removed from the denominator (never scored zero) and
  the adjusted maximum is stated.
- The results folder is readable and contains candidate submissions (checked
  in workflow step 1).

`scripts/check_gradebook.py profile <profile>` performs the arithmetic check.
If the gate fails, report each problem and stop. Proceed on failure only with
an explicit instructor override recorded in the run manifest.

## Workflow

1. **Inventory and attribute.** List the results folder recursively. Record each file's name, path, type, size, and hash. Match files to students, in order: exact roster name; reliable filename patterns; group membership evidenced inside the file; instructor confirmation. Count duplicate versions once. Never transfer evidence between students. Uncertain or absent submissions, and any file that cannot be attributed to a roster student, must stay visible as a `pending` record named from the file, with a reason — never silently dropped and never a zero for absence alone.
2. **Extract evidence.** Read submissions with the harness's tools (`scripts/extract_text.py` in OpenCode). Keep provenance for every observation: file plus page, sheet/cell/row, notebook cell, figure, or section. Never open excluded media.
3. **Verify independently.** Recompute rubric-critical numbers from the exam's own equations. Compare report claims against workbook/notebook outputs and source data. Record discrepancies with both values and locations.
4. **Score criterion by criterion.** Award partial credit for correct supported work. Tie every deduction to a criterion and observable evidence. Do not double-penalize one defect. Static numbers do not prove a working formula when the rubric requires implementation.
5. **Reconcile.** Sum per question and overall; the denominator uses only included criteria. Re-sum independently with zero tolerance. Keep pending students out of aggregates and mark them explicitly.
6. **Deliver.** Default destination `grading-run/` unless the instructor specifies another path:

   ```
   grading-run/
     profile.md        built rubric profile (audit trail)
     gradebook.json    internal format; convert to XLSX or CSV
     feedback.md       per-student evidence-linked feedback
     manifest.md       run manifest
   ```

   Write the XLSX gradebook (one row per student, one column per criterion, totals, percent, feedback reference, notes, plus a numerical-checks sheet) when a spreadsheet writer exists; otherwise CSV + Markdown. Never write into the results folder.
7. **Verify writes and record.** If a gradebook or report was written anywhere, read it back and confirm contents. Keep a run manifest: inputs, profile file, file hashes, assumptions, overrides, pending items, and any revision made after new evidence.

## Scoring rules

- The instructor's rubric and the built profile override any example in this skill.
- Judge only observable submitted evidence; cite exact locations.
- For numerical work, check formulas, units, stopping criteria, counts, rounding, and original-equation substitution when the rubric requires them.
- For charts and tables, check whether they answer the assigned question and agree with the underlying data.
- Inaccessible or unverifiable evidence leaves the affected score pending with an explanation, unless the rubric explicitly defines another treatment.
- Excluded evidence is never opened, never scored, and removed from the denominator; recompute the maximum from included criteria.

## References

- `references/rubric-profile-template.md` — canonical profile format; normally built by the skill from the instructor's rubric (fill manually only for overrides or non-OpenCode harnesses).
- `references/eda-numerical-methods-profile.md` — completed example for one exam. Do not reuse its weights for other exams.
- `references/provider-adapter.md` — harness mapping, including OpenCode specifics.
- `scripts/check_gradebook.py` — profile arithmetic and gradebook validation.
- `scripts/extract_text.py` — dependency-free text extraction for docx/xlsx/pdf/ipynb.

## Run manifest (keep with the run)

```
exam / questions source / rubric source / profile file
results folder / excluded evidence types / adjusted denominator
students scored and pending (with reasons)
assumptions and overrides
deliverable locations and read-back result
```
