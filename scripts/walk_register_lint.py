#!/usr/bin/env python3
"""Walk register validator — check fold-row tables against walk-register-schema v0.1.

Standalone, warn-only, not wired into any gate chain.
Read-only, standard library only. Emits TSV to stdout.

Usage:
    python walk_register_lint.py <path>

    <path>  a single walk-register file, or a directory to glob walk-register-*.md
"""

import re
import sys
from pathlib import Path

STATUS_PRE_SCHEMA = "PRE-SCHEMA"
STATUS_CONFORMANT = "CONFORMANT"
STATUS_UNCONFORMANT = "UNCONFORMANT"
STATUS_NO_TABLE = "NO_TABLE"

ROW_OK = "OK"
ROW_WARN = "WARN"

REQUIRED_COLUMNS = [
    "id", "walk", "lens", "sub_question", "origin",
    "finding", "pre_fold_text", "resolution",
]

SCHEMA_DECL_RE = re.compile(
    r"^\*\*schema_version:\*\*\s+`?([^`\n]+)`?\s*$", re.MULTILINE
)

FOLD_MARKERS = {"fold", "resolution", "pre_fold_text"}

TRUNCATION_RE = re.compile(r"\.\.\.|…")

COLUMNS = [
    "file", "line", "table", "row_status", "file_status",
    "columns", "missing", "note",
]
HEADER = "\t".join(COLUMNS)


def normalize_column(name):
    name = re.sub(r"\*\*", "", name)
    name = name.strip("`").strip()
    return name.lower().replace("-", "_").replace(" ", "_")


def is_fold_table(header_cells):
    normalized = {normalize_column(c) for c in header_cells}
    return "finding" in normalized and bool(normalized & FOLD_MARKERS)


def split_table_row(line):
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    inner = stripped[1:-1]
    cells = []
    current = []
    i = 0
    while i < len(inner):
        if inner[i] == "\\" and i + 1 < len(inner) and inner[i + 1] == "|":
            current.append("\\|")
            i += 2
        elif inner[i] == "|":
            cells.append("".join(current).strip())
            current = []
            i += 1
        else:
            current.append(inner[i])
            i += 1
    cells.append("".join(current).strip())
    return cells


def is_separator_row(cells):
    return all(re.match(r"^[-:]+$", c) for c in cells if c)


def unescape_pre_fold_text(text):
    result = []
    i = 0
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "|":
                result.append("|")
                i += 2
                continue
            elif nxt == "\\":
                result.append("\\")
                i += 2
                continue
        result.append(text[i])
        i += 1
    return "".join(result)


def escape_pre_fold_text(text):
    return text.replace("\\", "\\\\").replace("|", "\\|")


def has_schema_declaration(text):
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and "|" in stripped[1:]:
            cells = split_table_row(line)
            if cells and not is_separator_row(cells):
                return False
        if SCHEMA_DECL_RE.match(stripped):
            return True
    return False


def extract_tables(text):
    lines = text.splitlines()
    tables = []
    i = 0
    while i < len(lines):
        cells = split_table_row(lines[i])
        if cells is None or not cells:
            i += 1
            continue
        if is_separator_row(cells):
            i += 1
            continue
        header_cells = cells
        header_line = i + 1
        if i + 1 < len(lines):
            sep = split_table_row(lines[i + 1])
            if sep and is_separator_row(sep):
                data_rows = []
                j = i + 2
                while j < len(lines):
                    row_cells = split_table_row(lines[j])
                    if row_cells is None:
                        break
                    if is_separator_row(row_cells):
                        j += 1
                        continue
                    data_rows.append((j + 1, row_cells))
                    j += 1
                tables.append((header_cells, data_rows, header_line))
                i = j
                continue
        i += 1
    return tables


def validate_row(norm_cols, row_cells):
    missing = []
    notes = []

    if norm_cols != REQUIRED_COLUMNS:
        for req in REQUIRED_COLUMNS:
            if req not in norm_cols:
                missing.append(req)
        return ROW_WARN, missing, "wrong_shape"

    if len(row_cells) < len(REQUIRED_COLUMNS):
        for i in range(len(row_cells), len(REQUIRED_COLUMNS)):
            missing.append(REQUIRED_COLUMNS[i])

    pft_idx = REQUIRED_COLUMNS.index("pre_fold_text")

    for i, req in enumerate(REQUIRED_COLUMNS):
        if i < len(row_cells):
            val = row_cells[i].strip()
            if not val:
                missing.append(req)

    if missing:
        return ROW_WARN, missing, "missing_fields"

    pft_val = row_cells[pft_idx].strip()
    if pft_val != "ADDITION" and TRUNCATION_RE.search(pft_val):
        return ROW_WARN, ["pre_fold_text"], "truncated_pre_fold_text"

    return ROW_OK, [], "-"


def validate_file(filepath):
    text = filepath.read_text(encoding="utf-8")
    pre_schema = not has_schema_declaration(text)

    tables = extract_tables(text)
    fold_tables = []
    shapes = []
    for hdr, data, hline in tables:
        if is_fold_table(hdr):
            fold_tables.append((hdr, data, hline))
            shapes.append("| " + " | ".join(hdr) + " |")

    if not fold_tables:
        status = STATUS_PRE_SCHEMA if pre_schema else STATUS_NO_TABLE
        return status, [], shapes

    if pre_schema:
        file_status = STATUS_PRE_SCHEMA
    else:
        any_warn = False
        for hdr, data, _hline in fold_tables:
            norm = [normalize_column(c) for c in hdr]
            if norm != REQUIRED_COLUMNS:
                any_warn = True
                break
            for _, rcells in data:
                rs, _, _ = validate_row(norm, rcells)
                if rs == ROW_WARN:
                    any_warn = True
                    break
            if any_warn:
                break
        file_status = STATUS_UNCONFORMANT if any_warn else STATUS_CONFORMANT

    rows = []
    for tidx, (hdr, data, _hline) in enumerate(fold_tables, 1):
        norm = [normalize_column(c) for c in hdr]
        shape = "| " + " | ".join(hdr) + " |"
        for line_num, rcells in data:
            rs, miss, note = validate_row(norm, rcells)
            rows.append({
                "file": filepath.name,
                "line": str(line_num),
                "table": str(tidx),
                "row_status": rs,
                "file_status": file_status,
                "columns": shape,
                "missing": ",".join(miss) if miss else "-",
                "note": note,
            })

    return file_status, rows, shapes


def make_tsv_row(row_dict):
    return "\t".join(row_dict.get(c, "-") for c in COLUMNS)


def main():
    if len(sys.argv) < 2:
        print(
            f"Usage: {sys.argv[0]} <path>\n\n"
            "  <path>  a single walk-register file, or a directory\n"
            "          to glob walk-register-*.md",
            file=sys.stderr,
        )
        sys.exit(0)

    target = Path(sys.argv[1])

    if target.is_dir():
        files = sorted(target.glob("walk-register-*.md"))
        if not files:
            print(f"No walk-register-*.md found in {target}", file=sys.stderr)
            sys.exit(0)
    elif target.is_file():
        files = [target]
    else:
        print(f"ERROR: {target} not found", file=sys.stderr)
        sys.exit(1)

    print(HEADER)
    for fp in files:
        try:
            file_status, rows, shapes = validate_file(fp)
        except Exception as e:
            print(f"ERROR reading {fp}: {e}", file=sys.stderr)
            continue
        shape_str = " ; ".join(shapes) if shapes else "(none)"
        print(f"{fp.name}\t{file_status}\tshapes: {shape_str}", file=sys.stderr)
        for rd in rows:
            print(make_tsv_row(rd))


if __name__ == "__main__":
    main()
