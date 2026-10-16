# Validation checklist — strict-exam-output-grading

Run `python3 validation/run_validation.py` for the scripted checks. The items
below cover behavior that must also be verified in an agent grading run.

## Scripted (run_validation.py)

- [ ] Fixture generation succeeds and is deterministic.
- [ ] Good rubric profile passes the arithmetic check.
- [ ] Broken rubric profile (`rubric-profile-bad.md`) fails the arithmetic
      check; grading must not start on it without a recorded override.
- [ ] Canonical gradebook passes all checks against `expected_scores.json`.
- [ ] Corrupted gradebook copy fails (arithmetic or expected mismatch).
- [ ] Text extraction finds planted values in the generated docx/xlsx/pdf.
- [ ] The excluded mp4 is reported as non-extractable and is never read as a
      submission.

## Agent run (grading the fixture following SKILL.md)

- [ ] Readiness gate executed before scoring; scope and adjusted denominator
      (20, not 25) stated.
- [ ] Excluded media type (video/mp4) not opened or scored; excluded points
      removed from the denominator, not zeros.
- [ ] Nested submission found (`results/Cruz/`) before any missing marking.
- [ ] Duplicate version (`_duplicates/Gamma_Dana_Report.docx`) counted once.
- [ ] Pending cases stay pending with reasons and no numeric totals:
      Elle Delta (video only), Frank Echo (absent), unidentified submission.
- [ ] No zero assigned for absence alone.
- [ ] No evidence or scores transferred between students.
- [ ] Every graded criterion cites a concrete evidence location (file plus
      sheet/table/paragraph).
- [ ] Q2 prose claim with no iteration values earns no points (John Beta).
- [ ] Q2(b) not attempted earns no points (Charlie Cruz); other criteria keep
      full credit (no double deduction).
- [ ] Totals match `expected_scores.json`: Alpha 20, Beta 10, Cruz 15,
      Gamma 20; pending count 3.
- [ ] If a gradebook/report was written anywhere, it was read back and
      verified.
- [ ] No real student data present anywhere in the repo (synthetic only).
