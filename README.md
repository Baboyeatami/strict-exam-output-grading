# Strict Exam Output Grading (OpenCode skill)

Grade any exam from three inputs:

1. exam questions/instructions,
2. the instructor's rubric, and
3. a folder of student results (local or accessible; nested folders OK).

The skill defines the process; each exam's weights and criteria come from a
rubric profile filled for that exam. The EDA/EMATH 311 profile is a completed
example only — its weights are never applied to another exam.

## Contents

```
.opencode/skills/strict-exam-output-grading/
  SKILL.md                    workflow: inputs, readiness gate, scoring, delivers
  references/
    rubric-profile-template.md      fill one per exam (required before grading)
    eda-numerical-methods-profile.md  completed example (EMATH 311)
    provider-adapter.md             harness mapping incl. OpenCode + JSON shapes
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

## Install

- This repo: the skill is already discoverable by OpenCode here. Quit and
  restart OpenCode (skills load at startup; they are not hot-reloaded), then
  ask it to grade an exam.
- Any project: copy `.opencode/skills/strict-exam-output-grading/` into
  `<project>/.opencode/skills/` (restart OpenCode) or into
  `~/.config/opencode/skills/` for all projects.
- Other harnesses: use the folder (or `strict-exam-output-grading.zip`)
  as skill/context files; see `references/provider-adapter.md`.

## Use

Provide the skill with: exam questions, rubric, results folder; optionally a
roster, excluded media types (e.g. video), group rules, and the desired output
format. Default deliverable is an XLSX gradebook plus per-student feedback
(CSV + Markdown fallback). The skill runs a readiness gate first and stops on
rubric arithmetic problems instead of inventing weights.

Validate scripts and fixtures with:

```
python3 validation/run_validation.py
```

## Guarantees and boundaries

- Excluded media (video, etc.) is never opened or scored and is removed from
  the denominator — not counted as zeros.
- Missing, uncertain, or unattributable submissions stay pending (never zero,
  never silently dropped).
- Every deduction cites a criterion and an evidence location; no double
  deductions; partial credit where the rubric supports it.
- Nothing is written outside the requested deliverables, and every write is
  read back and verified.
- All fixtures in this repo are synthetic; keep real student data out of the
  repository.
