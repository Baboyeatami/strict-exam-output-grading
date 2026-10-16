#!/usr/bin/env python3
"""Validate rubric profile arithmetic and exam gradebooks (stdlib only).

Usage:
  python3 check_gradebook.py profile <profile.md>
  python3 check_gradebook.py gradebook <gradebook.json> [--expected expected_scores.json]

Profile checks:
  - criteria table rows parse (| Question | Criterion id | Criterion | Points | Evidence |)
  - per-question sums match 'Declared Q<N> total:' lines
  - overall sum matches the 'Declared total:' line
  - criterion ids are unique and points positive

Gradebook checks:
  - exam.max equals the sum of criterion maxima
  - scored students have every criterion, scores within [0, max], and
    total == sum of scores; percent == total / denominator * 100 (0-100 scale)
  - pending students carry no numeric totals or scores
  - with --expected: per-student totals, pending count, and denominator match

Expected file shape:
  {"denominator": 20, "scored": {"Alpha": 20, "Beta": 10}, "pending_count": 3}
  (scored keys are matched case-insensitively as substrings of student names)

Exit codes: 0 = all checks passed, 1 = one or more failures, 2 = usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

TOL = 1e-4
Q_RE = re.compile(r"^q?(\d+)$", re.IGNORECASE)


def close(a, b, tol=TOL):
    return abs(float(a) - float(b)) <= tol


class Report:
    def __init__(self):
        self.failures = []
        self.lines = []

    def ok(self, msg):
        self.lines.append("PASS  " + msg)

    def fail(self, msg):
        self.lines.append("FAIL  " + msg)
        self.failures.append(msg)

    def info(self, msg):
        self.lines.append("      " + msg)

    def print(self):
        for line in self.lines:
            print(line)


def parse_profile(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    errors = []
    declared_total = None
    m = re.search(r"Declared total:\s*([0-9]+(?:\.[0-9]+)?)", text)
    if m:
        declared_total = float(m.group(1))
    declared_q = {}
    for m in re.finditer(r"Declared\s+Q(\d+)\s+total:\s*([0-9]+(?:\.[0-9]+)?)", text):
        declared_q["Q" + m.group(1)] = float(m.group(2))
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        first = cells[0].lower()
        if first in ("question", "q") or first.startswith("---"):
            continue
        qm = Q_RE.match(cells[0])
        if not qm:
            continue
        q = "Q" + qm.group(1)
        cid = cells[1].strip("`")
        pts_raw = cells[3]
        try:
            pts = float(pts_raw)
        except ValueError:
            errors.append("row %s / %s has unparseable points: %r" % (q, cid, pts_raw))
            continue
        rows.append({"question": q, "id": cid, "points": pts})
    return declared_total, declared_q, rows, errors


def check_profile(path):
    rep = Report()
    declared_total, declared_q, rows, errors = parse_profile(path)
    for e in errors:
        rep.fail(e)
    if not rows:
        rep.fail("no criteria rows found (expected table: | Question | Criterion id | Criterion | Points | Evidence |)")
    ids = [r["id"] for r in rows]
    for d in sorted({i for i in ids if ids.count(i) > 1}):
        rep.fail("duplicate criterion id: %s" % d)
    for r in rows:
        if r["points"] <= 0:
            rep.fail("criterion %s has non-positive points" % r["id"])
    sums = {}
    for r in rows:
        sums[r["question"]] = sums.get(r["question"], 0.0) + r["points"]
    for q, total in sorted(declared_q.items()):
        if q not in sums:
            rep.fail("declared %s total %g but no criteria rows exist for it" % (q, total))
        elif not close(sums[q], total):
            rep.fail("%s criteria sum to %g but declared total is %g" % (q, sums[q], total))
    for q in sorted(sums):
        if declared_q and q not in declared_q:
            rep.info("note: %s has criteria but no 'Declared %s total:' line" % (q, q))
    overall = sum(sums.values())
    if declared_total is None:
        rep.fail("missing 'Declared total:' line")
    elif not close(overall, declared_total):
        rep.fail("criteria sum to %g but declared total is %g" % (overall, declared_total))
    if not rep.failures:
        rep.ok(
            "profile arithmetic consistent: %d criteria, %s, total %g"
            % (len(rows), ", ".join("%s=%g" % (q, sums[q]) for q in sorted(sums)), overall)
        )
    rep.print()
    return 0 if not rep.failures else 1


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check_gradebook(path, expected_path=None):
    rep = Report()
    gb = load_json(path)
    students = gb.get("students") or []
    crit = gb.get("criteria") or []
    cids = [c.get("id") for c in crit]
    cmax = {c.get("id"): float(c.get("max", 0)) for c in crit}
    for d in sorted({i for i in cids if cids.count(i) > 1}):
        rep.fail("duplicate criterion id: %s" % d)
    for c in crit:
        if float(c.get("max", 0)) <= 0:
            rep.fail("criterion %s has non-positive max" % c.get("id"))
    total_max = sum(cmax.values())
    exam_max = (gb.get("exam") or {}).get("max")
    if exam_max is not None and not close(exam_max, total_max):
        rep.fail("exam.max %g != sum of criterion maxima %g" % (float(exam_max), total_max))
    denom = float(exam_max) if exam_max is not None else total_max
    scored_totals = []
    pending_count = 0
    for st in students:
        name = st.get("name", "?")
        status = str(st.get("status", "")).lower()
        if status == "scored":
            scores = st.get("scores") or {}
            for cid in cids:
                if cid not in scores:
                    rep.fail("%s missing score for %s" % (name, cid))
            for cid, val in scores.items():
                if cid not in cmax:
                    rep.fail("%s has unknown criterion %s" % (name, cid))
                    continue
                if not isinstance(val, (int, float)):
                    rep.fail("%s score for %s is not numeric" % (name, cid))
                elif not (-TOL <= float(val) <= cmax[cid] + TOL):
                    rep.fail(
                        "%s score for %s (%g) outside [0, %g]" % (name, cid, float(val), cmax[cid])
                    )
            ssum = sum(float(v) for v in scores.values() if isinstance(v, (int, float)))
            total = st.get("total")
            if not isinstance(total, (int, float)):
                rep.fail("%s scored but total is not numeric" % name)
            else:
                if not close(total, ssum):
                    rep.fail("%s total %g != sum of scores %g" % (name, float(total), ssum))
                if denom > 0:
                    pct = st.get("percent")
                    if pct is not None and not isinstance(pct, (int, float)):
                        rep.fail("%s percent is not numeric" % name)
                    elif isinstance(pct, (int, float)) and not close(
                        float(pct), float(total) / denom * 100.0, tol=1e-2
                    ):
                        rep.fail(
                            "%s percent %g != total/denominator*100 (%.4f)"
                            % (name, float(pct), float(total) / denom * 100.0)
                        )
                scored_totals.append(float(total))
        elif status == "pending":
            pending_count += 1
            if st.get("total") is not None or st.get("percent") is not None:
                rep.fail("%s pending but has numeric total/percent" % name)
            scores = st.get("scores") or {}
            if any(v is not None for v in scores.values()):
                rep.fail("%s pending but has scores" % name)
        else:
            rep.fail("%s has unknown status %r (expected scored or pending)" % (name, st.get("status")))
    if expected_path:
        exp = load_json(expected_path)
        if "denominator" in exp and not close(exp["denominator"], denom):
            rep.fail("denominator %g != expected %g" % (denom, float(exp["denominator"])))
        exp_scored = exp.get("scored", {})
        exp_totals = []
        for key, want in sorted(exp_scored.items()):
            matches = [
                st
                for st in students
                if key.lower() in str(st.get("name", "")).lower()
                and str(st.get("status", "")).lower() == "scored"
            ]
            if not matches:
                rep.fail("expected scored student matching %r not found" % key)
                continue
            st = matches[0]
            if not close(st.get("total"), want):
                rep.fail("expected %s total %g, got %s" % (key, float(want), st.get("total")))
            exp_totals.append(float(want))
        if "pending_count" in exp and pending_count != int(exp["pending_count"]):
            rep.fail("pending count %d != expected %d" % (pending_count, int(exp["pending_count"])))
        got = sorted(scored_totals)
        want = sorted(exp_totals)
        if len(got) != len(want) or any(not close(a, b) for a, b in zip(got, want)):
            rep.fail("scored totals %s != expected %s" % (got, want))
    if not rep.failures:
        rep.ok(
            "gradebook passed: %d students (%d scored, %d pending), denominator %g"
            % (len(students), len(scored_totals), pending_count, denom)
        )
    rep.print()
    return 0 if not rep.failures else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate rubric profiles and exam gradebooks.")
    sub = ap.add_subparsers(dest="mode", required=True)
    p1 = sub.add_parser("profile", help="check rubric profile arithmetic")
    p1.add_argument("path")
    p2 = sub.add_parser("gradebook", help="check a gradebook JSON")
    p2.add_argument("path")
    p2.add_argument("--expected", help="expected_scores.json to compare against")
    args = ap.parse_args(argv)
    if args.mode == "profile":
        return check_profile(args.path)
    return check_gradebook(args.path, args.expected)


if __name__ == "__main__":
    sys.exit(main())
