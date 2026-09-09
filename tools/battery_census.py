#!/usr/bin/env python3
"""
tools/battery_census.py — read-only census over the walk-register corpus.

For each walk-register-*.md, emits one TSV row:
  slug, date, session, walks, finding_rows, fold_introduced, fold_rate,
  plan_lint, cycle_check, fold_check, propagation_check,
  walk_register_lint, mutation_check, lifecycle_state, tableless,
  lens_order, validation_line, coverage

Recording codes per tool: verbatim / paraphrase / not_recorded

Imports walk_register_lint (the shipped parser) for table extraction and
coverage_verdict; imports lens_order_check for the lens_order column.
Shims around the sub_q -> sub_question gap (disclosed walk 4: normalize_column
does not map the live sub_q variant, defect in a shipped instrument).

Usage:
    python tools/battery_census.py [--registers DIR] [--db PATH] [--json]
"""

import io
import json
import re
import sqlite3
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import lens_order_check as loc
import walk_register_lint as wrl

DEFAULT_REGISTERS = Path("/Users/marklehn/Developer/eluvian-governance/governance/knowledge/research")
DEFAULT_DB = ROOT / "lifecycle.db"

BATTERY_TOOLS = [
    "plan_lint", "cycle_check", "fold_check",
    "propagation_check", "walk_register_lint", "mutation_check",
]

# sub_q shim: wrl.normalize_column maps sub_q -> sub_q (does not fix it)
SUB_Q_SHIM = {"sub_q": "sub_question"}


def shim_normalize(name):
    normed = wrl.normalize_column(name)
    return SUB_Q_SHIM.get(normed, normed)


# ── field extractors ──────────────────────────────────────────────────────────

SESSION_RE = re.compile(r"\(session\s+`([0-9a-f]{7,8})`")
WALK_HEADING_RE = re.compile(r"^#{1,3}\s+Walk\s+(\d+)\b", re.MULTILINE)
DATE_FROM_FNAME_RE = re.compile(r"(\d{4}-\d{2}-\d{2})\.md$")
PLAN_LINE_RE = re.compile(r"\*\*Plan:\*\*\s+`[^`]*?([^/`]+\.md)`")
DRAFT_LINE_RE = re.compile(r"\bDraft:\s+`[^`]*/([^/`]+\.md)`")
FOLD_INTRODUCED_RE = re.compile(r"fold.introduced", re.IGNORECASE)
VALIDATION_RE = re.compile(r"^validation: cycle_check=", re.MULTILINE)


def extract_session(text):
    m = SESSION_RE.search(text)
    return m.group(1) if m else ""


def extract_walk_count(text):
    nums = {int(m.group(1)) for m in WALK_HEADING_RE.finditer(text)}
    return max(nums) + 1 if nums else 0


def extract_plan_placeholder(text):
    """Extract deposit_placeholder_name from the **Plan:** line (bold format)."""
    m = PLAN_LINE_RE.search(text)
    if not m:
        return ""
    return m.group(1).strip()


def extract_draft_placeholder(text):
    """Extract deposit_placeholder_name from Draft: line, fallback to **Plan:** line."""
    m = DRAFT_LINE_RE.search(text)
    if m:
        return m.group(1).strip()
    return extract_plan_placeholder(text)


def extract_tables_by_name(text):
    """Return list of {cols, rows} for fold tables, indexed by header NAME."""
    tables, _ = wrl.extract_tables(text)
    result = []
    for hdr, data, _hline in tables:
        if not wrl.is_fold_table(hdr):
            continue
        norm_cols = [shim_normalize(c) for c in hdr]
        rows = []
        for _linenum, cells in data:
            row = {}
            for i, col in enumerate(norm_cols):
                row[col] = cells[i].strip() if i < len(cells) else ""
            rows.append(row)
        result.append({"cols": norm_cols, "rows": rows})
    return result


def count_findings(tables):
    finding_rows = fold_introduced = 0
    for tbl in tables:
        for row in tbl["rows"]:
            finding_rows += 1
            origin = row.get("origin", "")
            if FOLD_INTRODUCED_RE.search(origin):
                fold_introduced += 1
    return finding_rows, fold_introduced


# ── battery detection ─────────────────────────────────────────────────────────
# Verbatim: tool name appears backtick-quoted followed by a machine output token
# (exit code, verdict string, numeric result).
# Paraphrase: tool name appears but output is prose or absent.
# Detection is conservative: a false "not_recorded" is safer than a false "verbatim".

_VERBATIM = {
    "plan_lint": re.compile(
        r"`plan_lint`\s*(exit\s*\d|→\s*(PASS|FAIL|WARN)|\d+\s*(PASS|FAIL|WARN))",
        re.IGNORECASE,
    ),
    "cycle_check": re.compile(
        r"`cycle_check`\s*(→|exit\s*\d)\s*(BAR_MET|CONTINUE|ESCALATE|FAIL|0|1)",
        re.IGNORECASE,
    ),
    "fold_check": re.compile(
        r"`fold_check`\s*(→\s*(PASS|FAIL)|--save-baseline|readers=|\d+\s*readers)",
        re.IGNORECASE,
    ),
    "propagation_check": re.compile(
        r"`propagation_check`\s*(exit\s*\d|\d+\s*divergences|→\s*(PASS|FAIL|0|1))",
        re.IGNORECASE,
    ),
    "walk_register_lint": re.compile(
        r"`walk_register_lint`\s*(CONFORMANT|UNCONFORMANT|NO_TABLE|PRE.SCHEMA|LEGACY|→)",
        re.IGNORECASE,
    ),
    "mutation_check": re.compile(
        r"`mutation_check`\s*(→\s*(PASS|FAIL|KILLED|SURVIVED)|exit\s*\d|\d+\s*mutant)",
        re.IGNORECASE,
    ),
}

_NAMED = {
    tool: re.compile(r"`?" + re.escape(tool) + r"`?", re.IGNORECASE)
    for tool in BATTERY_TOOLS
}


def detect_battery(text):
    result = {}
    for tool in BATTERY_TOOLS:
        if _VERBATIM[tool].search(text):
            result[tool] = "verbatim"
        elif _NAMED[tool].search(text):
            result[tool] = "paraphrase"
        else:
            result[tool] = "not_recorded"
    return result


# ── lifecycle lookup ──────────────────────────────────────────────────────────

def load_lifecycle(db_path):
    """Return dict: deposit_placeholder_name -> (lifecycle_state, plan_doc_ref)."""
    db = Path(db_path)
    if not db.exists():
        return {}
    conn = sqlite3.connect(str(db))
    try:
        rows = conn.execute(
            "SELECT deposit_placeholder_name, lifecycle_state, plan_doc_ref FROM plans"
        ).fetchall()
    except sqlite3.OperationalError:
        return {}
    finally:
        conn.close()
    return {r[0]: (r[1], r[2]) for r in rows if r[0]}


def lookup_lifecycle(placeholder, lifecycle_map):
    if not placeholder:
        return "unknown"
    entry = lifecycle_map.get(placeholder)
    if entry:
        return entry[0]
    # Try adding type prefixes
    for prefix in ("diagnostic-", "executable-", "qa-"):
        candidate = prefix + placeholder
        if candidate in lifecycle_map:
            return lifecycle_map[candidate][0]
    return "unknown"


def lookup_plan_doc_ref(placeholder, lifecycle_map):
    """Return plan_doc_ref string or None."""
    if not placeholder:
        return None
    entry = lifecycle_map.get(placeholder)
    if entry:
        return entry[1]
    for prefix in ("diagnostic-", "executable-", "qa-"):
        candidate = prefix + placeholder
        if candidate in lifecycle_map:
            return lifecycle_map[candidate][1]
    return None


# ── new-column helpers ────────────────────────────────────────────────────────

_lens_order_cache: dict = {}


def get_lens_order(plan_doc_ref, root):
    """Run lens_order_check on the Done plan and return the verdict token."""
    if not plan_doc_ref:
        return "unresolved"
    if plan_doc_ref in _lens_order_cache:
        return _lens_order_cache[plan_doc_ref]
    plan_path = root / plan_doc_ref
    if not plan_path.exists():
        _lens_order_cache[plan_doc_ref] = "unresolved"
        return "unresolved"
    buf = io.StringIO()
    try:
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            loc.main([str(plan_path)])
    except Exception:
        _lens_order_cache[plan_doc_ref] = "unresolved"
        return "unresolved"
    output = buf.getvalue()
    verdict = "unresolved"
    for line in output.splitlines():
        if "LENS-ORDER OK" in line:
            verdict = "OK"
            break
        elif "LENS-ORDER N/A" in line:
            verdict = "N/A"
            break
        elif line.startswith("NO-RECORD"):
            verdict = "NO-RECORD"
            break
        elif line.startswith("BATCHED"):
            verdict = "BATCHED"
            break
        elif line.startswith("INCOMPLETE"):
            verdict = "INCOMPLETE"
            break
        elif line.startswith("UNPROVEN"):
            verdict = "UNPROVEN"
            break
    _lens_order_cache[plan_doc_ref] = verdict
    return verdict


def get_validation_line(plan_doc_ref, root):
    """Return 'yes' if the Done plan carries validation: cycle_check=, else 'no'."""
    if not plan_doc_ref:
        return "no"
    plan_path = root / plan_doc_ref
    if not plan_path.exists():
        return "no"
    try:
        text = plan_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return "no"
    return "yes" if VALIDATION_RE.search(text) else "no"


def get_coverage(text, fp):
    """Return the COVERAGE verdict token from walk_register_lint.coverage_verdict."""
    try:
        token, _ = wrl.coverage_verdict(text, fp)
        return token
    except Exception:
        return "unresolved"


# ── per-file processor ────────────────────────────────────────────────────────

COLUMNS = [
    "slug", "date", "session", "walks", "finding_rows", "fold_introduced", "fold_rate",
    "plan_lint", "cycle_check", "fold_check", "propagation_check",
    "walk_register_lint", "mutation_check",
    "lifecycle_state", "tableless",
    "lens_order", "validation_line", "coverage",
]


def process_file(fp, lifecycle_map):
    slug = fp.stem.removeprefix("walk-register-")
    m = DATE_FROM_FNAME_RE.search(fp.name)
    date = m.group(1) if m else "no-date"

    text = fp.read_text(encoding="utf-8")
    session = extract_session(text)
    walks = extract_walk_count(text)
    placeholder = extract_plan_placeholder(text)
    lifecycle_state = lookup_lifecycle(placeholder, lifecycle_map)

    # Draft placeholder (Draft: first, fallback to **Plan:**) for new columns
    draft_placeholder = extract_draft_placeholder(text)
    plan_doc_ref = lookup_plan_doc_ref(draft_placeholder, lifecycle_map)

    tables = extract_tables_by_name(text)
    tableless = len(tables) == 0
    finding_rows, fold_introduced = count_findings(tables)
    fold_rate = fold_introduced / finding_rows if finding_rows else 0.0

    battery = detect_battery(text)

    lens_order = get_lens_order(plan_doc_ref, ROOT)
    validation_line = get_validation_line(plan_doc_ref, ROOT)
    coverage = get_coverage(text, fp)

    return {
        "slug": slug,
        "date": date,
        "session": session,
        "walks": walks,
        "finding_rows": finding_rows,
        "fold_introduced": fold_introduced,
        "fold_rate": f"{fold_rate:.3f}",
        "plan_lint": battery["plan_lint"],
        "cycle_check": battery["cycle_check"],
        "fold_check": battery["fold_check"],
        "propagation_check": battery["propagation_check"],
        "walk_register_lint": battery["walk_register_lint"],
        "mutation_check": battery["mutation_check"],
        "lifecycle_state": lifecycle_state,
        "tableless": "yes" if tableless else "no",
        "lens_order": lens_order,
        "validation_line": validation_line,
        "coverage": coverage,
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Walk-register corpus census")
    parser.add_argument("--registers", default=str(DEFAULT_REGISTERS),
                        help="Directory containing walk-register-*.md files")
    parser.add_argument("--db", default=str(DEFAULT_DB),
                        help="Path to lifecycle.db")
    parser.add_argument("--json", action="store_true",
                        help="Emit JSON array instead of TSV")
    args = parser.parse_args()

    registers_dir = Path(args.registers)
    files = sorted(registers_dir.glob("walk-register-*.md"))

    lifecycle_map = load_lifecycle(args.db)

    rows = []
    errors = []
    for fp in files:
        try:
            rows.append(process_file(fp, lifecycle_map))
        except Exception as exc:
            errors.append(f"ERROR {fp.name}: {exc}")

    for e in errors:
        print(e, file=sys.stderr)

    if args.json:
        print(json.dumps(rows, indent=2))
        return

    # TSV
    print("\t".join(COLUMNS))
    for row in rows:
        print("\t".join(str(row.get(c, "")) for c in COLUMNS))

    # Summary
    total = len(rows)
    tableless_n = sum(1 for r in rows if r["tableless"] == "yes")
    has_session = sum(1 for r in rows if r["session"])
    print(f"\n=== CORPUS SUMMARY ===", file=sys.stderr)
    print(f"Total registers: {total}", file=sys.stderr)
    print(f"Tableless (no fold table): {tableless_n}", file=sys.stderr)
    print(f"With session ID: {has_session}", file=sys.stderr)
    print(file=sys.stderr)
    for tool in BATTERY_TOOLS:
        v = sum(1 for r in rows if r[tool] == "verbatim")
        p = sum(1 for r in rows if r[tool] == "paraphrase")
        n = sum(1 for r in rows if r[tool] == "not_recorded")
        print(f"  {tool:25s}  verbatim={v:3d}  paraphrase={p:3d}  not_recorded={n:3d}",
              file=sys.stderr)
    print(file=sys.stderr)
    total_fi = sum(int(r["fold_introduced"]) for r in rows)
    total_fr = sum(int(r["finding_rows"]) for r in rows)
    print(f"Corpus-wide: {total_fr} finding rows, {total_fi} fold-introduced "
          f"({total_fi/total_fr:.1%} of tabled rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
