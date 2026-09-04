"""Tier-2 test suite for scripts/propagation_check.py.

State space (sixteen cells):
  symbol form {bold-backtick / row-id} ×
  value-cell form {plain-backtick / plain} ×
  {hex present / absent} ×
  {date present / absent}

Plus: legacy bold-numeral positive control, exit-2 path, detector-(1) hit
and qualifier-suppression, sha-256 exclusion, and report-format check.
"""
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

import propagation_check as pc


@pytest.fixture(autouse=True)
def reset_declaring_lines():
    pc._DECLARING_LINES.clear()
    yield
    pc._DECLARING_LINES.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

HEX = "ab9aa01d50142b45"   # 16-char hex token — must be excluded
DATE = "2026-09-02"         # ISO date — must be excluded
NUMVAL = "1782"             # the expected numeric value in every cell


def _plan_text(rows, prose=""):
    header = "| pin | what | value | how |\n|---|---|---|---|\n"
    return (
        "# Plan\n\n## Numbers\n\n"
        + header
        + "\n".join(rows)
        + "\n\n## Steps\n\n"
        + prose
        + "\n\n## Drafting Cycle\n\nw1 dry.\n"
    )


def _run(plan_text, tmp_path, name="plan.md"):
    p = tmp_path / name
    p.write_text(plan_text, encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(BELLOWS_ROOT / "scripts" / "propagation_check.py"),
         str(p)],
        capture_output=True, text=True, timeout=30,
    )
    return r


# ---------------------------------------------------------------------------
# Sixteen-cell cross-product
# ---------------------------------------------------------------------------

def _make_row(sym_bold, val_backtick, with_hex, with_date):
    extras = (f" {HEX}" if with_hex else "") + (f" {DATE}" if with_date else "")
    val_part = (f"`{NUMVAL}`" if val_backtick else NUMVAL) + extras
    sym_cell = "**`SYM`**" if sym_bold else "P1"
    first = "P1"
    return f"| {first} | {sym_cell} | {val_part} |"


CELLS = [
    (sym_bold, val_backtick, with_hex, with_date)
    for sym_bold in (True, False)
    for val_backtick in (True, False)
    for with_hex in (True, False)
    for with_date in (True, False)
]


def test_cross_product_completeness():
    """All sixteen symbol×value×hex×date combinations are in CELLS."""
    assert len(CELLS) == 16
    expected = {
        (s, v, h, d)
        for s in (True, False)
        for v in (True, False)
        for h in (True, False)
        for d in (True, False)
    }
    assert set(CELLS) == expected


@pytest.mark.parametrize("sym_bold,val_backtick,with_hex,with_date", CELLS)
def test_sixteen_cells(sym_bold, val_backtick, with_hex, with_date):
    """NUMVAL is parsed; HEX and DATE numerals are excluded."""
    row = _make_row(sym_bold, val_backtick, with_hex, with_date)
    decls = pc.declared_values(_plan_text([row]))
    expected_sym = "SYM" if sym_bold else "P1"
    assert expected_sym in decls, f"symbol not found in {decls!r}\nrow: {row}"
    assert NUMVAL in decls[expected_sym], (
        f"value {NUMVAL!r} not in {decls[expected_sym]!r}\nrow: {row}"
    )
    # date parts must NOT appear as extracted values
    for date_part in ("2026", "02", "09"):
        if len(date_part) >= 2 and with_date:
            assert date_part not in decls.get(expected_sym, []), (
                f"date numeral {date_part!r} leaked into values\nrow: {row}"
            )


# ---------------------------------------------------------------------------
# Dedicated kill-map targets (M1 and M2)
# ---------------------------------------------------------------------------

def test_hex_excluded():
    """M1 kill: 12+-char hex token — no digit-runs extracted."""
    row = f"| P1 | **`SHA`** | {HEX} |"
    decls = pc.declared_values(_plan_text([row]))
    # All numerals inside a hex token must be masked; SHA has no surviving values
    assert "SHA" not in decls


def test_row_id_symbol():
    """M2 kill: row-id-only form — the row id becomes the symbol."""
    row = "| P3 | plain name | 51 |"
    decls = pc.declared_values(_plan_text([row]))
    assert "P3" in decls
    assert "51" in decls["P3"]


# ---------------------------------------------------------------------------
# Exit-2 path
# ---------------------------------------------------------------------------

def test_exit2_no_numerals(tmp_path):
    """A table with no 2+-digit numerals exits 2 (could not run)."""
    r = _run("# Plan\n\n| P1 | SYM | text only |\n", tmp_path)
    assert r.returncode == 2


# ---------------------------------------------------------------------------
# Legacy bold-numeral positive control
# ---------------------------------------------------------------------------

def test_legacy_bold_numeral():
    """`| N1 | **`BATCH`** | — | **25** |` → BATCH: ['25']."""
    text = "# Plan\n\n| N1 | **`BATCH`** | — | **25** |\n"
    decls = pc.declared_values(text)
    assert "BATCH" in decls
    assert "25" in decls["BATCH"]


# ---------------------------------------------------------------------------
# Detector-(1) hit and qualifier suppression
# ---------------------------------------------------------------------------

def test_detector1_hit(tmp_path):
    """Value restated in prose without a qualifier triggers a divergence."""
    plan = (
        "# Plan\n\n"
        "| P1 | **`SUITE`** | 1782 |\n\n"
        "## Steps\n\n"
        "Run all 1782 tests and verify they pass.\n"
    )
    r = _run(plan, tmp_path)
    assert r.returncode == 1
    assert "DIVERGENCES" in r.stdout


def test_detector1_qualifier_suppression(tmp_path):
    """A restatement within 90 chars of a qualifier is NOT a divergence."""
    plan = (
        "# Plan\n\n"
        "| P1 | **`SUITE`** | 1782 |\n\n"
        "## Steps\n\n"
        "The suite was 1782 tests as measured at walk 0.\n"
    )
    r = _run(plan, tmp_path)
    assert r.returncode == 0


# ---------------------------------------------------------------------------
# sha-256 / -a 256 exclusion
# ---------------------------------------------------------------------------

def test_sha256_context_excluded():
    """256 appearing in 'sha-256' or '-a 256' is not extracted as a value."""
    row = "| P1 | **`SRC`** | shasum -a 256 out.txt |"
    decls = pc.declared_values(_plan_text([row]))
    assert "SRC" not in decls or "256" not in decls.get("SRC", [])


# ---------------------------------------------------------------------------
# Report format
# ---------------------------------------------------------------------------

def test_line_reference_is_not_a_declared_value():
    """thread 96 form 1: `file.ext:NNN` is a location, not a quantity.

    Measured 2026-09-04 over 86 plans: 276 of 1444 extracted values (19%) were of
    this form, and each one then flagged every later mention of that number as a
    restatement — the false-positive flood that made the tool unreadable.
    """
    vals = pc._cell_numerals(
        "the guard at `bellows.py:1179` and its sibling `:1317`"
    )
    assert vals == [], vals


def test_identifier_word_numeral_is_not_a_declared_value():
    """thread 96 form 2: a numeral introduced by an identifier word is a NAME."""
    vals = pc._cell_numerals(
        "per thread 119 and Rule 34, superseded by plan 520"
    )
    assert vals == [], vals


def test_a_real_declaration_survives_both_qualifiers():
    """⛔ The negative control. A colon-with-space is a DECLARATION, not a location,
    and a bare quantity beside identifier words must still be extracted."""
    vals = pc._cell_numerals(
        "threads: 90 open; the census counted 1444 values across 86 plans"
    )
    assert "90" in vals and "1444" in vals and "86" in vals, vals


def test_report_line_format(tmp_path):
    """First stdout line is 'declared symbols: N (values: M)'."""
    plan = "# Plan\n\n| P1 | **`SUITE`** | 1782 |\n\n## Drafting Cycle\nw1 dry.\n"
    r = _run(plan, tmp_path)
    first = r.stdout.splitlines()[0]
    assert first.startswith("declared symbols: "), first
    assert "(values:" in first, first
