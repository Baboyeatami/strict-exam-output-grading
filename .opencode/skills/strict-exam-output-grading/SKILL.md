---
name: strict-exam-output-grading
description: Grade or audit exam submissions from a results folder against instructor-supplied exam questions and a rubric. Use when asked to check, score, or grade student exam files (docx, xlsx, pdf, notebooks, images) or to prepare a gradebook and per-student feedback. Handles rubric readiness checks, partial credit, pending/ambiguous submissions, excluded media such as videos, and independent numerical verification.
---

# Strict exam output grading

Grade an exam from three inputs: the exam questions, the instructor's rubric, and a folder of student results. This file defines the process; every exam's weights, criteria, and evidence rules come from a rubric profile filled for that exam (`references/rubric-profile-template.md`). A profile from another exam must never be reused as a default.

## Inputs

Required:

1. Exam questions/instructions.
2. Rubric with criteria and points.
3. Results folder (local or otherwise accessible; may contain nested subfolders).

Optional: roster, excluded evidence types (for example video), group-work rules, deliverable format preference, destination for the gradebook.

Ask only when a required input is missing or the readiness gate fails. Do not invent weights, criteria, answers, or submissions.

## Readiness gate

Fill one rubric profile for this exam before grading. Verify:

- Every question has criteria with points; points sum to each question's declared maximum and to the exam total.
- Every criterion maps to a question and to an observable artifact (file, sheet, section, figure).
- The results folder exists, is readable, and contains candidate submissions.
- Excluded evidence types are recorded. Criteria that can only be met through excluded evidence are removed from the denominator, not scored as zero; state the adjusted maximum.

Run `scripts/check_gradebook.py profile <profile>` for the arithmetic. If arithmetic or coverage fails, report each problem and stop. Proceed only on an explicit instructor override, recorded in the run manifest.

## Workflow

1. **Inventory and attribute.** List the results folder recursively. Record each file's name, path, type, size, and hash. Match files to students, in order: exact roster name; reliable filename patterns; group membership evidenced inside the file; instructor confirmation. Count duplicate versions once. Never transfer evidence between students. Uncertain or absent submissions, and any file that cannot be attributed to a roster student, must stay visible as a `pending` record named from the file, with a reason — never silently dropped and never a zero for absence alone.
2. **Extract evidence.** Read submissions with the harness's tools (`scripts/extract_text.py` in OpenCode). Keep provenance for every observation: file plus page, sheet/cell/row, notebook cell, figure, or section. Never open excluded media.
3. **Verify independently.** Recompute rubric-critical numbers from the exam's own equations. Compare report claims against workbook/notebook outputs and source data. Record discrepancies with both values and locations.
4. **Score criterion by criterion.** Award partial credit for correct supported work. Tie every deduction to a criterion and observable evidence. Do not double-penalize one defect. Static numbers do not prove a working formula when the rubric requires implementation.
5. **Reconcile.** Sum per question and overall; the denominator uses only included criteria. Re-sum independently with zero tolerance. Keep pending students out of aggregates and mark them explicitly.
6. **Deliver.** Default: XLSX gradebook (one row per student, one column per criterion, totals, percent, feedback reference, notes, plus a numerical-checks sheet) and concise per-student feedback with evidence. Fall back to CSV + Markdown when no spreadsheet writer exists. Do not write to any destination the instructor did not request.
7. **Verify writes and record.** If a gradebook or report was written anywhere, read it back and confirm contents. Keep a run manifest: inputs, profile, file hashes, assumptions, overrides, pending items, and any revision made after new evidence.

## Scoring rules

- The instructor's rubric and the filled profile override any example in this skill.
- Judge only observable submitted evidence; cite exact locations.
- For numerical work, check formulas, units, stopping criteria, counts, rounding, and original-equation substitution when the rubric requires them.
- For charts and tables, check whether they answer the assigned question and agree with the underlying data.
- Inaccessible or unverifiable evidence leaves the affected score pending with an explanation, unless the rubric explicitly defines another treatment.
- Excluded evidence is never opened, never scored, and removed from the denominator; recompute the maximum from included criteria.

## References

- `references/rubric-profile-template.md` — fill one per exam; required before grading.
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
