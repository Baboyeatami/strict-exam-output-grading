# Provider and harness adapter contract

The grading logic is independent of any specific model or tool provider. Map
the operations below to the target harness's file, document, spreadsheet, and
computation tools. Replace only this mapping when changing harnesses; keep the
rubric profile, evidence standard, and scoring process unchanged.

## Inputs the harness should expose

- Exam questions and the authoritative rubric.
- Results folder path/link (local or mounted; Drive only when a connector is
  configured).
- Optional roster, scope instructions (including excluded media types), and
  requested deliverable format/destination.

## Capabilities

1. List the requested folder and descendants, preserving file names, paths,
   IDs/links, and parent relationships.
2. Retrieve or read supported files without modifying the source submission.
3. Read PDFs, office documents, spreadsheets, notebooks, images, or other
   relevant formats. If a format is unsupported, report the limitation and use
   an available export/preview path.
4. Preserve evidence references: file name/link plus page, sheet/cell, notebook
   cell, figure, or section where possible.
5. Independently calculate or check rubric-relevant quantities.
6. If explicitly requested, create/update the destination gradebook/report and
   read it back to verify the saved contents.

## OpenCode mapping

- Skill discovery: `.opencode/skills/<name>/SKILL.md` (project) or
  `~/.config/opencode/skills/<name>/SKILL.md` (global). The folder name must
  match the frontmatter `name`. Skills load at startup; restart OpenCode after
  installing or editing. No `opencode.json` change is needed for the project
  location.
- Folder listing and search: `glob`, `grep`, and shell commands via `bash`.
- Text extraction: `python3 scripts/extract_text.py <file>...` (stdlib only;
  handles docx, xlsx, pdf with uncompressed or FlateDecode text, ipynb, and
  plain-text formats). For images, inspect visually only when permitted.
- Verification math: `python3` stdlib (`math`, `decimal`, `json`); recompute
  from raw values, never from the student's cached results alone.
- Gradebook validation: `python3 scripts/check_gradebook.py gradebook
  <gradebook.json> [--expected <expected_scores.json>]` and
  `python3 scripts/check_gradebook.py profile <profile.md>`.
- Writing deliverables: the `write` tool; read back with `read`. Spreadsheet
  writers may not be available — fall back to CSV + Markdown and say so.
- Drive or other remote storage: only when an MCP/connector is configured.
  Local files are the default and the only requirement.
- Video, audio, and other excluded media: do not open, decode, or score.

## Suggested evidence record

Keep one internal record per student and criterion:

```text
student_id_or_name:
submission_files: [name + path/link + sha256]
criterion:
points_awarded / points_possible:
evidence_location:
observed_evidence:
reason_for_credit_or_deduction:
uncertainty_or_follow_up:
```

Do not place private tool logs or unsupported assumptions in student-facing
feedback. Keep evidence records available for instructor verification.

## Gradebook JSON (default internal format)

`scripts/check_gradebook.py` validates this shape; convert it to XLSX/CSV for
the instructor.

```json
{
  "exam": {"title": "...", "max": 20, "excluded": ["video"]},
  "criteria": [{"id": "q1_a", "question": "Q1", "max": 5}],
  "students": [
    {"name": "...", "status": "scored", "scores": {"q1_a": 5}, "total": 20, "percent": 100.0, "notes": ""},
    {"name": "...", "status": "pending", "scores": {}, "total": null, "percent": null, "notes": "only video, excluded"}
  ]
}
```

Rules: scored students must have every criterion scored; pending students have
no numeric totals; the exam maximum equals the sum of criterion maxima.

## Portability

- In an Agent Skills-compatible harness, load the skill folder so `SKILL.md`
  is discovered and keep the references alongside it.
- In a harness without skill support, provide `SKILL.md` plus the filled
  profile as task instructions or context files.
- A different model does not change the rubric; it must not authorize
  unsupported inference. Keep student data and grading evidence out of public
  examples; use synthetic data for tests.
