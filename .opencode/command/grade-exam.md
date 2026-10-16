---
description: Grade an exam from questions + rubric + a folder of student outputs
agent: build
---

Grade an exam using the `strict-exam-output-grading` skill. First read and
follow `.opencode/skills/strict-exam-output-grading/SKILL.md`.

User-provided arguments (may be partial or empty):
$ARGUMENTS

Intake rules:

- Inputs, in order: (1) exam questions and rubric (files or text; the rubric
  may be inside the questions document), (2) the results folder.
- If inputs are missing, request them in that order and wait. Do not start
  grading with a missing input.
- Build the rubric profile from the instructor's rubric automatically,
  validate it with `.opencode/skills/strict-exam-output-grading/scripts/check_gradebook.py profile`,
  and continue automatically when the rubric is explicit and the gate passes.
  Stop and ask only for genuine ambiguity (missing points, unmapped criteria,
  unclear exclusions, or arithmetic failure).
- Write outputs to `./grading-run/` unless another destination is specified.
  Never write into the results folder.

Finish with: the built profile, the gradebook (XLSX or CSV + Markdown),
per-student feedback, and the run manifest — with any written file read back
and verified.
