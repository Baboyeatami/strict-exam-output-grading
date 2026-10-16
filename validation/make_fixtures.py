#!/usr/bin/env python3
"""Generate the synthetic fixture files for skill validation (stdlib only).

Creates validation/fixture-exam/results/ from scratch (idempotent). All data
is synthetic; no real student information is used.

Files generated:
  Alpha_Jane_Report.docx          full values, all four methods
  Alpha_Jane_Workbook.xlsx        full values, four sheets
  Beta_John_Report.docx           Q1 values only; Q2 prose claim without values
  Cruz/Charlie_Report.pdf         Q1 values; Q2(a) values; Q2(b) not completed
  Cruz/Charlie_Workbook.xlsx      Q1 sheets + Q2_Secant only
  Gamma_Dana_Report.docx          full values (duplicate copy below)
  _duplicates/Gamma_Dana_Report.docx  byte-identical duplicate
  delta_video.mp4                 excluded media (fake video bytes)
  unknown_submission.docx         no identity; must stay pending
"""
from __future__ import annotations

import io
import shutil
import zipfile
from pathlib import Path

FIX = Path(__file__).resolve().parent / "fixture-exam"
RESULTS = FIX / "results"

FIXED_DATE = (2026, 1, 1, 0, 0, 0)

Q1_BISECTION = [
    ["Bisection f(x)=x^3-x-2 on [1,2], tolerance 0.05"],
    ["iter", "a", "b", "mid", "f(mid)", "width"],
    [1, 1, 2, 1.5, -0.125, 0.5],
    [2, 1.5, 2, 1.75, 1.609375, 0.25],
    [3, 1.5, 1.75, 1.625, 0.666016, 0.125],
    [4, 1.5, 1.625, 1.5625, 0.252197, 0.0625],
    [5, 1.5, 1.5625, 1.53125, 0.059113, 0.03125],
    ["final root", 1.515625],
]

Q1_NEWTON = [
    ["Newton-Raphson f(x)=x^3-x-2 from x0=1.5"],
    ["iter", "x", "f(x)", "f'(x)", "x_next"],
    [1, 1.5, -0.125, 5.75, 1.521739],
    [2, 1.521739, 0.001991, 5.94707, 1.521404],
    ["final root", 1.521404],
]

Q2_SECANT = [
    ["Secant g(x)=x^3-2x-5 with x0=2, x1=3"],
    ["n", "x_n", "g(x_n)"],
    [0, 2, -1],
    [1, 3, 16],
    [2, 2.058824, -0.390888],
    [3, 2.081269, -0.147203],
    [4, 2.094828, 0.003177],
    [5, 2.094541, -0.000031],
    ["final root", 2.094541],
]

Q2_FALSEPOS = [
    ["False Position g(x)=x^3-2x-5 on [2,3]"],
    ["iter", "a", "b", "x_FP", "g(x_FP)"],
    [1, 2, 3, 2.058824, -0.390888],
    [2, 2.058824, 3, 2.081271, -0.147204],
    [3, 2.081271, 3, 2.089646, -0.069583],
    ["final root", 2.089646],
]


def _esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def make_docx_bytes(paragraphs):
    body = "".join(
        '<w:p><w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p>' % _esc(p)
        for p in paragraphs
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>%s</w:body></w:document>" % body
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(zipfile.ZipInfo("[Content_Types].xml", FIXED_DATE), content_types)
        z.writestr(zipfile.ZipInfo("_rels/.rels", FIXED_DATE), rels)
        z.writestr(zipfile.ZipInfo("word/document.xml", FIXED_DATE), document)
    return buf.getvalue()


def col_letter(n):
    letters = ""
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def make_xlsx_bytes(sheets):
    sheet_xml = []
    workbook_sheets = []
    workbook_rels = []
    content_overrides = []
    for i, (name, rows) in enumerate(sheets, start=1):
        xml_rows = []
        for r, row in enumerate(rows, start=1):
            cells = []
            for c, val in enumerate(row, start=1):
                ref = "%s%d" % (col_letter(c), r)
                if isinstance(val, (int, float)):
                    cells.append('<c r="%s"><v>%s</v></c>' % (ref, val))
                else:
                    cells.append(
                        '<c r="%s" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                        % (ref, _esc(val))
                    )
            xml_rows.append('<row r="%d">%s</row>' % (r, "".join(cells)))
        sheet_xml.append(
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                "<sheetData>%s</sheetData></worksheet>" % "".join(xml_rows)
            )
        )
        workbook_sheets.append(
            '<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (_esc(name), i, i)
        )
        workbook_rels.append(
            '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>'
            % (i, i)
        )
        content_overrides.append(
            '<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            % i
        )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        "%s</Types>" % "".join(content_overrides)
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "<sheets>%s</sheets></workbook>" % "".join(workbook_sheets)
    )
    workbook_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        "%s</Relationships>" % "".join(workbook_rels)
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(zipfile.ZipInfo("[Content_Types].xml", FIXED_DATE), content_types)
        z.writestr(zipfile.ZipInfo("_rels/.rels", FIXED_DATE), rels)
        z.writestr(zipfile.ZipInfo("xl/workbook.xml", FIXED_DATE), workbook)
        z.writestr(zipfile.ZipInfo("xl/_rels/workbook.xml.rels", FIXED_DATE), workbook_rels_xml)
        for i, xml in enumerate(sheet_xml, start=1):
            z.writestr(zipfile.ZipInfo("xl/worksheets/sheet%d.xml" % i, FIXED_DATE), xml)
    return buf.getvalue()


def make_pdf_bytes(lines):
    def esc(s):
        return str(s).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    parts = ["BT /F1 11 Tf 50 750 Td 16 TL"]
    for line in lines:
        parts.append("(%s) Tj T*" % esc(line))
    parts.append("ET")
    content = "\n".join(parts).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += ("%d 0 obj\n" % i).encode("latin-1") + obj + b"\nendobj\n"
    xref_pos = len(out)
    out += ("xref\n0 %d\n" % (len(objects) + 1)).encode("latin-1")
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += ("%010d 00000 n \n" % off).encode("latin-1")
    out += (
        "trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
        % (len(objects) + 1, xref_pos)
    ).encode("latin-1")
    return bytes(out)


JANE_REPORT = [
    "EMATH 100 Make-Up Quiz - Report",
    "Student: Jane Alpha",
    "Question 1a - Bisection on [1,2], tolerance 0.05. Midpoints: 1.5, 1.75, 1.625, 1.5625, 1.53125. Bracket width after 5 iterations is 0.03125 < 0.05. Final root: 1.515625.",
    "Question 1b - Newton-Raphson from x0=1.5. Iteration values: x1=1.521739, x2=1.521404. Final root: 1.521404.",
    "Question 2a - Secant with x0=2, x1=3. Iteration values: 2.058824, 2.081269, 2.094828, 2.094541. Final root: 2.094541.",
    "Question 2b - False Position on [2,3]. Iteration values: 2.058824, 2.081271, 2.089646. Final root: 2.089646.",
    "The same values are in the submitted workbook.",
]

JOHN_REPORT = [
    "EMATH 100 Make-Up Quiz - Report",
    "Student: John Beta",
    "Question 1a - Bisection on [1,2]. Midpoints: 1.5, 1.75, 1.625, 1.5625, 1.53125. Final root: 1.515625.",
    "Question 1b - Newton-Raphson from x0=1.5. Iteration values: x1=1.521739, x2=1.521404. Final root: 1.521404.",
    "Question 2a - Secant converged to about 2.09. See analysis.",
    "Question 2b - False Position also converged to about 2.09.",
    "No workbook was uploaded; the Q2 summary is from my rough notes.",
]

CHARLIE_PDF = [
    "EMATH 100 Make-Up Quiz - Report",
    "Student: Charlie Cruz",
    "Q1a Bisection on [1,2], tolerance 0.05. Midpoints: 1.5, 1.75, 1.625, 1.5625, 1.53125. Final root: 1.515625.",
    "Q1b Newton-Raphson from 1.5. x1=1.521739, x2=1.521404. Final root: 1.521404.",
    "Q2a Secant with x0=2, x1=3. Iteration values: 2.058824, 2.081269, 2.094828, 2.094541. Final root: 2.094541.",
    "Q2b False Position on [2,3]: not completed.",
    "Workbook includes the Q1 and Q2a sheets.",
]

DANA_REPORT = [
    "EMATH 100 Make-Up Quiz - Report",
    "Student: Dana Gamma",
    "Question 1a - Bisection on [1,2], tolerance 0.05. Midpoints: 1.5, 1.75, 1.625, 1.5625, 1.53125. Final root: 1.515625.",
    "Question 1b - Newton-Raphson from x0=1.5. Iteration values: x1=1.521739, x2=1.521404. Final root: 1.521404.",
    "Question 2a - Secant with x0=2, x1=3. Iteration values: 2.058824, 2.081269, 2.094828, 2.094541. Final root: 2.094541.",
    "Question 2b - False Position on [2,3]. Iteration values: 2.058824, 2.081271, 2.089646. Final root: 2.089646.",
]

UNKNOWN_REPORT = [
    "My answer for the quiz.",
    "I used bisection and got about 1.5 but did not finish the rest.",
]


def main():
    if RESULTS.exists():
        shutil.rmtree(RESULTS)
    (RESULTS / "Cruz").mkdir(parents=True)
    (RESULTS / "_duplicates").mkdir(parents=True)

    (RESULTS / "Alpha_Jane_Report.docx").write_bytes(make_docx_bytes(JANE_REPORT))
    (RESULTS / "Alpha_Jane_Workbook.xlsx").write_bytes(
        make_xlsx_bytes(
            [
                ("Q1_Bisection", Q1_BISECTION),
                ("Q1_Newton", Q1_NEWTON),
                ("Q2_Secant", Q2_SECANT),
                ("Q2_FalsePosition", Q2_FALSEPOS),
            ]
        )
    )

    (RESULTS / "Beta_John_Report.docx").write_bytes(make_docx_bytes(JOHN_REPORT))

    (RESULTS / "Cruz" / "Charlie_Report.pdf").write_bytes(make_pdf_bytes(CHARLIE_PDF))
    (RESULTS / "Cruz" / "Charlie_Workbook.xlsx").write_bytes(
        make_xlsx_bytes(
            [
                ("Bisection_Q1", Q1_BISECTION),
                ("Newton_Q1", Q1_NEWTON),
                ("Secant_Q2", Q2_SECANT),
            ]
        )
    )

    dana_bytes = make_docx_bytes(DANA_REPORT)
    (RESULTS / "Gamma_Dana_Report.docx").write_bytes(dana_bytes)
    (RESULTS / "_duplicates" / "Gamma_Dana_Report.docx").write_bytes(dana_bytes)

    (RESULTS / "delta_video.mp4").write_bytes(
        b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom" + b"\x00" * 64
    )

    (RESULTS / "unknown_submission.docx").write_bytes(make_docx_bytes(UNKNOWN_REPORT))

    print("fixtures written to %s" % RESULTS)
    for path in sorted(RESULTS.rglob("*")):
        if path.is_file():
            print("  %s (%d bytes)" % (path.relative_to(FIX), path.stat().st_size))


if __name__ == "__main__":
    main()
