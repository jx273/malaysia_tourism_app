"""Minimal .xlsx reader built on the standard library only.

DOSM publishes its tourism statistics as formatted Excel reports, not as tidy tables:
one workbook holds several numbered tables, headers are bilingual and span merged
cells, and the sheet layout changes between editions. Rather than add a dependency,
this module returns each sheet as a list of rows of trimmed cell strings and lets
``clean.py`` locate the tables it needs. Blank cells are dropped, so a row is the
sequence of values that actually carry content.

Only the parts of the format DOSM's files use are handled: shared strings, inline
strings, and numeric cells. Formulas are read as their cached values.

Used by: src/clean.py
"""
from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

_T = f"{{{MAIN_NS}}}t"
_V = f"{{{MAIN_NS}}}v"
_C = f"{{{MAIN_NS}}}c"
_ROW = f"{{{MAIN_NS}}}row"


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(_T)) for si in root.findall(f"{{{MAIN_NS}}}si")]


def _sheet_targets(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    """Return [(sheet name, zip path)] in the workbook's own order."""
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    by_id = {r.get("Id"): r.get("Target") for r in rels.findall(f"{{{PKG_REL_NS}}}Relationship")}
    out = []
    for sheet in workbook.find(f"{{{MAIN_NS}}}sheets").findall(f"{{{MAIN_NS}}}sheet"):
        target = by_id[sheet.get(f"{{{REL_NS}}}id")].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        out.append((sheet.get("name"), target))
    return out


def _rows(archive: zipfile.ZipFile, target: str, shared: list[str]) -> list[list[str]]:
    root = ET.fromstring(archive.read(target))
    rows = []
    for row in root.iter(_ROW):
        values = []
        for cell in row.findall(_C):
            kind = cell.get("t")
            value = cell.find(_V)
            if kind == "s" and value is not None:
                values.append(shared[int(value.text)])
            elif kind == "inlineStr":
                values.append("".join(t.text or "" for t in cell.iter(_T)))
            elif value is not None:
                values.append(value.text)
        values = [v.strip() for v in values if v is not None and v.strip()]
        if values:
            rows.append(values)
    return rows


def read_sheets(path: str | Path) -> dict[str, list[list[str]]]:
    """Read a workbook into {sheet name: [[cell, ...], ...]}, blank cells dropped."""
    with zipfile.ZipFile(path) as archive:
        shared = _shared_strings(archive)
        return {name: _rows(archive, target, shared) for name, target in _sheet_targets(archive)}


def first_sheet(path: str | Path) -> list[list[str]]:
    """Rows of the workbook's first sheet."""
    with zipfile.ZipFile(path) as archive:
        shared = _shared_strings(archive)
        name, target = _sheet_targets(archive)[0]
        return _rows(archive, target, shared)


def year_header(rows: list[list[str]], minimum: int = 4) -> list[str]:
    """The first row containing at least ``minimum`` four-digit years, as strings.

    DOSM tables put their year header two or three rows below the title, and the
    number of leading title rows is not consistent between editions, so the header
    is found by shape rather than by position.
    """
    for row in rows:
        years = [c for c in row if c.isdigit() and len(c) == 4]
        if len(years) >= minimum:
            return years
    return []
