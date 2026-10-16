#!/usr/bin/env python3
"""Dump readable text from common submission formats (stdlib only).

Supports:
  .docx  - Word documents
  .xlsx / .xlsm - Excel workbooks (cell values as A1=value lines)
  .pdf   - uncompressed or FlateDecode text operators (naive, good for
           generated/text PDFs; scanned pages are not OCR'd)
  .ipynb - Jupyter notebooks (cells and text outputs)
  .txt .md .csv .json .py .html .xml .tex .log - plain text

Anything else (images, video, archives) is reported as not text-extractable.

Usage: python3 extract_text.py FILE [FILE ...]
"""
from __future__ import annotations

import json
import os
import re
import sys
import zipfile
import zlib
from xml.etree import ElementTree


def _localname(tag):
    return tag.rsplit("}", 1)[-1]


def text_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    paragraphs = []
    for para in root.iter():
        if _localname(para.tag) != "p":
            continue
        parts = [t.text or "" for t in para.iter() if _localname(t.tag) == "t"]
        paragraphs.append("".join(parts))
    return "\n".join(paragraphs)


def text_xlsx(path):
    out = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        shared = []
        if "xl/sharedStrings.xml" in names:
            sroot = ElementTree.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sroot.iter():
                if _localname(si.tag) == "si":
                    shared.append(
                        "".join(t.text or "" for t in si.iter() if _localname(t.tag) == "t")
                    )
        sheet_names = {}
        if "xl/workbook.xml" in names:
            wroot = ElementTree.fromstring(z.read("xl/workbook.xml"))
            idx = 0
            for el in wroot.iter():
                if _localname(el.tag) == "sheet":
                    idx += 1
                    sheet_names[idx] = el.get("name") or ("Sheet%d" % idx)
        sheets = sorted(n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n))
        for name in sheets:
            num = int(re.search(r"(\d+)", name.split("/")[-1]).group(1))
            out.append("### sheet: %s" % sheet_names.get(num, "Sheet%d" % num))
            root = ElementTree.fromstring(z.read(name))
            for row in root.iter():
                if _localname(row.tag) != "row":
                    continue
                cells = []
                for c in row:
                    if _localname(c.tag) != "c":
                        continue
                    ref = c.get("r", "")
                    ctype = c.get("t")
                    val = ""
                    if ctype == "inlineStr":
                        val = "".join(
                            t.text or "" for t in c.iter() if _localname(t.tag) == "t"
                        )
                    else:
                        v = next((e for e in c if _localname(e.tag) == "v"), None)
                        if v is not None and v.text is not None:
                            if ctype == "s":
                                try:
                                    val = shared[int(v.text)]
                                except (ValueError, IndexError):
                                    val = v.text
                            else:
                                val = v.text
                    if val != "":
                        cells.append("%s=%s" % (ref, val))
                if cells:
                    out.append("  ".join(cells))
    return "\n".join(out)


def _pdf_strings(chunk):
    try:
        text = chunk.decode("latin-1")
    except Exception:
        return ""
    pieces = []
    for m in re.finditer(r"\((?:[^()\\]|\\.)*\)", text):
        s = m.group(0)[1:-1]
        s = re.sub(
            r"\\([nrtbf()\\])",
            lambda mm: {"n": "\n", "r": "\r", "t": "\t", "b": "", "f": ""}.get(
                mm.group(1), mm.group(1)
            ),
            s,
        )
        pieces.append(s)
    return " ".join(pieces)


def text_pdf(path):
    with open(path, "rb") as fh:
        data = fh.read()
    out = []
    for m in re.finditer(rb"stream\r?\n", data):
        start = m.end()
        end = data.find(b"endstream", start)
        if end == -1:
            continue
        raw = data[start:end]
        try:
            chunk = zlib.decompress(raw)
        except Exception:
            chunk = raw
        piece = _pdf_strings(chunk)
        if piece:
            out.append(piece)
    return "\n".join(out)


def text_ipynb(path):
    with open(path, encoding="utf-8") as fh:
        nb = json.load(fh)
    out = []
    for i, cell in enumerate(nb.get("cells", [])):
        out.append("--- cell %d (%s) ---" % (i + 1, cell.get("cell_type", "?")))
        out.append("".join(cell.get("source", [])))
        for o in cell.get("outputs", []) or []:
            if "text" in o:
                out.append("[output] " + "".join(o["text"]))
            data = o.get("data") or {}
            if "text/plain" in data:
                out.append("[output] " + "".join(data["text/plain"]))
    return "\n".join(out)


TEXT_EXTS = {".txt", ".md", ".csv", ".json", ".py", ".html", ".htm", ".xml", ".tex", ".log"}


def text_plain(path):
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8", errors="replace")


def extract(path):
    low = path.lower()
    if low.endswith(".docx"):
        return text_docx(path)
    if low.endswith(".xlsx") or low.endswith(".xlsm"):
        return text_xlsx(path)
    if low.endswith(".pdf"):
        return text_pdf(path)
    if low.endswith(".ipynb"):
        return text_ipynb(path)
    base = os.path.basename(low)
    ext = "." + base.rsplit(".", 1)[-1] if "." in base else ""
    if ext in TEXT_EXTS:
        return text_plain(path)
    size = os.path.getsize(path)
    return (
        "[binary or unsupported format, %d bytes - not text-extractable; "
        "inspect visually only if permitted]" % size
    )


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    rc = 0
    for path in argv:
        print("=" * 5 + " " + path + " " + "=" * 5)
        try:
            print(extract(path))
        except FileNotFoundError:
            print("ERROR: file not found", file=sys.stderr)
            rc = 1
        except Exception as exc:  # noqa: BLE001 - report and continue with next file
            print("ERROR: %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
            rc = 1
        print()
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
