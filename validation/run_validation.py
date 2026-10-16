#!/usr/bin/env python3
"""Run the scripted validation suite for strict-exam-output-grading.

Usage: python3 validation/run_validation.py

Checks:
  1. Fixture generation succeeds.
  2. Good rubric profile passes admission arithmetic.
  3. Broken rubric profile fails.
  4. EDA example profile still passes its declared arithmetic (88).
  5. Canonical gradebook passes all checks against expected_scores.json.
  6. A corrupted gradebook fails.
  7. Text extraction finds planted values in docx/xlsx/pdf fixtures.
  8. The excluded mp4 is reported non-extractable (never read as a submission).

Exit code 0 = all checks passed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SKILL = REPO / ".opencode" / "skills" / "strict-exam-output-grading"
FIX = ROOT / "fixture-exam"
RUN = ROOT / "run"
PY = sys.executable
CHECK = SKILL / "scripts" / "check_gradebook.py"
EXTRACT = SKILL / "scripts" / "extract_text.py"


def run(*args):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True)


def main():
    RUN.mkdir(exist_ok=True)
    failures = []

    def check(name, cond, detail=""):
        print("%s  %s%s" % ("PASS" if cond else "FAIL", name, (" - " + detail) if detail else ""))
        if not cond:
            failures.append(name)

    def one_line(text):
        return " | ".join(line for line in text.strip().splitlines() if line.strip())

    r = run(PY, ROOT / "make_fixtures.py")
    check("fixture generation", r.returncode == 0, one_line(r.stderr or r.stdout))

    r = run(PY, CHECK, "profile", FIX / "rubric-profile.md")
    check("good profile passes arithmetic", r.returncode == 0, one_line(r.stdout))

    r = run(PY, CHECK, "profile", FIX / "rubric-profile-bad.md")
    check("bad profile fails arithmetic", r.returncode == 1, one_line(r.stdout))

    r = run(PY, CHECK, "profile", SKILL / "references" / "eda-numerical-methods-profile.md")
    check("EDA example profile passes (88)", r.returncode == 0, one_line(r.stdout))

    r = run(PY, CHECK, "gradebook", ROOT / "expected_gradebook.json", "--expected", ROOT / "expected_scores.json")
    check("expected gradebook passes vs expected_scores", r.returncode == 0, one_line(r.stdout))

    bad_path = RUN / "corrupted_gradebook.json"
    gb = json.loads((ROOT / "expected_gradebook.json").read_text())
    gb["students"][0]["total"] = 19.0
    bad_path.write_text(json.dumps(gb, indent=2))
    r = run(PY, CHECK, "gradebook", bad_path, "--expected", ROOT / "expected_scores.json")
    check("corrupted gradebook fails", r.returncode == 1, one_line(r.stdout))

    r = run(PY, EXTRACT, FIX / "results" / "Alpha_Jane_Workbook.xlsx")
    check("xlsx extraction finds secant final root", r.returncode == 0 and "2.094541" in r.stdout)

    r = run(PY, EXTRACT, FIX / "results" / "Alpha_Jane_Report.docx")
    check("docx extraction finds bisection final root", r.returncode == 0 and "1.515625" in r.stdout)

    r = run(PY, EXTRACT, FIX / "results" / "Cruz" / "Charlie_Report.pdf")
    check("pdf extraction finds Q2a values", r.returncode == 0 and "2.058824" in r.stdout, one_line(r.stdout)[:120])

    r = run(PY, EXTRACT, FIX / "results" / "Beta_John_Report.docx")
    check("docx extraction finds John Q2 prose", r.returncode == 0 and "about 2.09" in r.stdout)

    r = run(PY, EXTRACT, FIX / "rubric.md")
    check(
        "raw instructor rubric extraction works",
        r.returncode == 0 and "20 points" in r.stdout and "5 points" in r.stdout,
    )

    mp4 = FIX / "results" / "delta_video.mp4"
    before = mp4.read_bytes()
    r = run(PY, EXTRACT, mp4)
    after = mp4.read_bytes()
    check(
        "mp4 reported non-extractable and untouched",
        r.returncode == 0 and "not text-extractable" in r.stdout and before == after,
    )

    print()
    if failures:
        print("VALIDATION FAILED: %d check(s): %s" % (len(failures), ", ".join(failures)))
        return 1
    print("VALIDATION PASSED: all scripted checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
