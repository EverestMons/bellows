"""Tests for walk_register_lint.py — all fixtures constructed, never live registers."""

import sys
import textwrap
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

# Force-load from the worktree's scripts/ so the full suite doesn't pick up
# a stale version cached by depositor.py (which uses resolve_bellows_root()).
import importlib  # noqa: E402
_WRL_PATH = str(BELLOWS_ROOT / "scripts" / "walk_register_lint.py")
if "walk_register_lint" in sys.modules and sys.modules["walk_register_lint"].__file__ != _WRL_PATH:
    importlib.reload(sys.modules["walk_register_lint"])

from walk_register_lint import (
    REQUIRED_COLUMNS,
    ROW_OK,
    ROW_WARN,
    STATUS_CONFORMANT,
    STATUS_NO_TABLE,
    STATUS_PRE_SCHEMA,
    STATUS_UNCONFORMANT,
    escape_pre_fold_text,
    has_schema_declaration,
    is_fold_table,
    normalize_column,
    split_table_row,
    unescape_pre_fold_text,
    validate_file,
    validate_row,
)
try:
    from walk_register_lint import STATUS_LEGACY_SCHEMA, STATUS_FUTURE_SCHEMA
except ImportError:
    STATUS_LEGACY_SCHEMA = "LEGACY_SCHEMA"
    STATUS_FUTURE_SCHEMA = "FUTURE_SCHEMA"


def _write_register(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# --- conformant row ---


CONFORMANT_REGISTER = """\
# Walk Register — test

**schema_version:** `0.3`

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| f1 | 1 | Weak spots | 1.1 | pre-existing | bad count | the exact bytes | fixed count |
| f2 | 1 | Destruction | 2.1 | fold-introduced | stale ref | old ref text | new ref |
"""


def test_conformant_row(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", CONFORMANT_REGISTER)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_CONFORMANT
    assert len(rows) == 2
    assert all(r["row_status"] == ROW_OK for r in rows)
    assert all(r["file_status"] == STATUS_CONFORMANT for r in rows)


# --- missing pre_fold_text (C2 — constructed, WARN must fire) ---


MISSING_PFT_REGISTER = """\
# Walk Register — test

**schema_version:** `0.3`

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| f1 | 1 | Weak spots | 1.1 | pre-existing | bad count | the bytes | fixed |
| f2 | 1 | Destruction | 2.1 | fold-introduced | stale ref | | new ref |
"""


def test_missing_pre_fold_text_warns(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", MISSING_PFT_REGISTER)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_UNCONFORMANT
    warn_rows = [r for r in rows if r["row_status"] == ROW_WARN]
    assert len(warn_rows) == 1
    assert "pre_fold_text" in warn_rows[0]["missing"]
    assert warn_rows[0]["note"] == "missing_fields"


# --- two-shape file ---


TWO_SHAPE_REGISTER = """\
# Walk Register — test

**schema_version:** `0.3`

## Walk 1

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| f1 | 1 | Weak spots | 1.1 | pre-existing | bad | old | fixed |

## Walk 2

| # | finding | fold |
|---|---|---|
| 1 | something | fixed it |
"""


def test_two_shape_file(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", TWO_SHAPE_REGISTER)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_UNCONFORMANT
    assert len(shapes) == 2
    table_nums = {r["table"] for r in rows}
    assert "1" in table_nums
    assert "2" in table_nums
    table2_rows = [r for r in rows if r["table"] == "2"]
    assert all(r["row_status"] == ROW_WARN for r in table2_rows)
    assert all("wrong_shape" in r["note"] for r in table2_rows)


# --- no table at all ---


NO_TABLE_REGISTER = """\
# Walk Register — test

**schema_version:** `0.3`

No tables here. Just prose describing the walk.
"""


def test_no_table_file(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", NO_TABLE_REGISTER)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_NO_TABLE
    assert rows == []


# --- no schema_version → PRE-SCHEMA ---


PRE_SCHEMA_REGISTER = """\
# Walk Register — test

No schema_version declaration here.

| # | sub-q | finding | fold |
|---|---|---|---|
| 1 | 1.1 | bad count | fixed |
"""


def test_pre_schema_status(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", PRE_SCHEMA_REGISTER)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_PRE_SCHEMA
    assert all(r["file_status"] == STATUS_PRE_SCHEMA for r in rows)


# --- PRE-SCHEMA with multi-shape: shapes are still reported ---


PRE_SCHEMA_MULTI_SHAPE = """\
# Walk Register — test

| # | sub-q | finding | fold |
|---|---|---|---|
| 1 | 1.1 | bad | fixed |

| # | finding | resolution |
|---|---|---|
| 2 | other | also fixed |
"""


def test_pre_schema_multi_shape(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", PRE_SCHEMA_MULTI_SHAPE)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_PRE_SCHEMA
    assert len(shapes) == 2


# --- schema_version in prose only (not a declaration) → PRE-SCHEMA ---


SCHEMA_VERSION_IN_PROSE = """\
# Walk Register — test

The schema_version field is described in the schema document.

It says to use **schema_version:** somewhere before the first table,
but this file only mentions it in prose.

| # | finding | fold |
|---|---|---|
| 1 | bad | fixed |
"""


def test_schema_version_in_prose_is_pre_schema(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", SCHEMA_VERSION_IN_PROSE)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_PRE_SCHEMA


# --- pipe round-trip ---


def test_pipe_escape_round_trip():
    original = "foo|bar"
    escaped = escape_pre_fold_text(original)
    assert escaped == "foo\\|bar"
    assert unescape_pre_fold_text(escaped) == original


# --- backslash round-trip ---


def test_backslash_escape_round_trip():
    original = "foo\\bar"
    escaped = escape_pre_fold_text(original)
    assert escaped == "foo\\\\bar"
    assert unescape_pre_fold_text(escaped) == original


# --- \\| sequence round-trip (the ambiguity case) ---


def test_backslash_pipe_escape_round_trip():
    original = "foo\\|bar"
    escaped = escape_pre_fold_text(original)
    assert escaped == "foo\\\\\\|bar"
    assert unescape_pre_fold_text(escaped) == original


# --- unescaped pipe corrupts the row ---


def test_unescaped_pipe_corrupts_row():
    row_with_escaped = "| f1 | 1 | WS | 1.1 | pre | bad | foo\\|bar | fixed |"
    cells = split_table_row(row_with_escaped)
    assert cells is not None
    assert len(cells) == 8
    assert cells[6] == "foo\\|bar"

    row_without_escape = "| f1 | 1 | WS | 1.1 | pre | bad | foo|bar | fixed |"
    cells_bad = split_table_row(row_without_escape)
    assert cells_bad is not None
    assert len(cells_bad) == 9  # corrupted — extra cell


# --- ADDITION literal ---


ADDITION_REGISTER = """\
# Walk Register — test

**schema_version:** `0.3`

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| f1 | 1 | Weak spots | 1.1 | fold-introduced | new guard | ADDITION | guard added |
"""


def test_addition_literal_conformant(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", ADDITION_REGISTER)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_CONFORMANT
    assert len(rows) == 1
    assert rows[0]["row_status"] == ROW_OK


# --- empty pre_fold_text (not ADDITION, not bytes) → WARN ---


EMPTY_PFT_REGISTER = """\
# Walk Register — test

**schema_version:** `0.3`

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| f1 | 1 | Weak spots | 1.1 | fold-introduced | new guard | | guard added |
"""


def test_empty_pre_fold_text_warns(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", EMPTY_PFT_REGISTER)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_UNCONFORMANT
    assert rows[0]["row_status"] == ROW_WARN
    assert "pre_fold_text" in rows[0]["missing"]


# --- truncated pre_fold_text (ellipsis) → WARN ---


TRUNCATED_PFT_REGISTER = """\
# Walk Register — test

**schema_version:** `0.3`

| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
|---|---|---|---|---|---|---|---|
| f1 | 1 | Weak spots | 1.1 | pre-existing | bad | the exact bytes... more | fixed |
"""


def test_truncated_pre_fold_text_warns(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", TRUNCATED_PFT_REGISTER)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_UNCONFORMANT
    assert rows[0]["row_status"] == ROW_WARN
    assert rows[0]["note"] == "truncated_pre_fold_text"


# --- non-fold tables are skipped ---


NON_FOLD_TABLE_REGISTER = """\
# Walk Register — test

**schema_version:** `0.3`

| field | required | meaning |
|---|---|---|
| id | yes | stable id |

| lens | folded | note |
|---|---|---|
| WS | 3 | first pass |
"""


def test_non_fold_tables_skipped(tmp_path):
    fp = _write_register(tmp_path, "walk-register-test.md", NON_FOLD_TABLE_REGISTER)
    status, rows, shapes = validate_file(fp)
    assert status == STATUS_NO_TABLE
    assert rows == []
    assert shapes == []


# --- normalize_column ---


def test_normalize_column_strips_markdown():
    assert normalize_column("**sub-q**") == "sub_q"
    assert normalize_column("`pre_fold_text`") == "pre_fold_text"
    assert normalize_column("sub question") == "sub_question"


# --- is_fold_table detection ---


def test_is_fold_table_positive():
    assert is_fold_table(["#", "finding", "fold"])
    assert is_fold_table(["#", "sub", "finding", "resolution"])
    assert is_fold_table(["id", "walk", "lens", "sub_question", "origin",
                          "finding", "pre_fold_text", "resolution"])


def test_is_fold_table_negative():
    assert not is_fold_table(["field", "required", "meaning"])
    assert not is_fold_table(["lens", "folded", "note"])
    assert not is_fold_table(["finding", "channel"])


# --- directory glob mode ---


def test_directory_glob(tmp_path):
    _write_register(tmp_path, "walk-register-a.md", CONFORMANT_REGISTER)
    _write_register(tmp_path, "walk-register-b.md", PRE_SCHEMA_REGISTER)
    _write_register(tmp_path, "not-a-register.md", CONFORMANT_REGISTER)

    from walk_register_lint import validate_file as vf

    a_status, a_rows, _ = vf(tmp_path / "walk-register-a.md")
    b_status, b_rows, _ = vf(tmp_path / "walk-register-b.md")
    assert a_status == STATUS_CONFORMANT
    assert b_status == STATUS_PRE_SCHEMA

    matches = sorted(tmp_path.glob("walk-register-*.md"))
    assert len(matches) == 2
    assert all("walk-register-" in m.name for m in matches)


# ---- v0.3 guards (wrl-guards-2026-08-13) ----

V03_HEADER = "**schema_version:** `0.3`\n\n"
FOLD_HEADER = (
    "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n"
    "|---|---|---|---|---|---|---|---|\n"
)


def _v03_file(tmp_path, body, name="walk-register-v03-fixture.md"):
    p = tmp_path / name
    p.write_text(V03_HEADER + body, encoding="utf-8")
    return p


def test_annotated_verbatim_ellipsis_is_ok(tmp_path):
    body = FOLD_HEADER + (
        "| f1 | 1 | ACID | 5.1 | pre-existing | prefix `abc…` is verbatim-ellipsis "
        "| pin `abc…` matched | kept |\n"
    )
    status, rows, _ = validate_file(_v03_file(tmp_path, body))
    assert status == "CONFORMANT"
    assert rows[0]["note"] == "verbatim_ellipsis_annotated"
    assert rows[0]["row_status"] == "OK"


def test_unannotated_ellipsis_still_warns(tmp_path):
    body = FOLD_HEADER + (
        "| f1 | 1 | ACID | 5.1 | pre-existing | elided | the guard ... elided | kept |\n"
    )
    status, rows, _ = validate_file(_v03_file(tmp_path, body))
    assert status == "UNCONFORMANT"
    assert rows[0]["note"] == "truncated_pre_fold_text"


def test_duplicate_row_warns_and_flips_status(tmp_path):
    row = "| f1 | 1 | ACID | 5.1 | pre-existing | dup | ADDITION | kept |\n"
    body = FOLD_HEADER + row + row
    status, rows, _ = validate_file(_v03_file(tmp_path, body))
    assert status == "UNCONFORMANT"
    assert any(r["note"] == "duplicate_row" for r in rows)


def test_repeated_table_header_is_not_duplicate_row(tmp_path):
    body = (
        FOLD_HEADER
        + "| f1 | 1 | ACID | 5.1 | pre-existing | a | ADDITION | kept |\n\n"
        + FOLD_HEADER
        + "| f2 | 2 | ACID | 5.1 | pre-existing | b | ADDITION | kept |\n"
    )
    status, rows, _ = validate_file(_v03_file(tmp_path, body))
    assert status == "CONFORMANT"
    assert not any(r["note"] == "duplicate_row" for r in rows)


def test_headerless_rows_warn_and_flip_status(tmp_path):
    body = (
        FOLD_HEADER
        + "| f1 | 1 | ACID | 5.1 | pre-existing | a | ADDITION | kept |\n"
        + "\nprose paragraph\n\n"
        + "| f2 | 2 | ACID | 5.1 | pre-existing | detached | ADDITION | kept |\n"
    )
    status, rows, _ = validate_file(_v03_file(tmp_path, body))
    assert status == "UNCONFORMANT"
    assert any(r["note"] == "headerless_rows" for r in rows)


def test_adjacent_duplicate_line_is_advisory_only(tmp_path):
    body = (
        FOLD_HEADER
        + "| f1 | 1 | ACID | 5.1 | pre-existing | a | ADDITION | kept |\n\n"
        + "the open tail line\nthe open tail line\n"
    )
    status, rows, _ = validate_file(_v03_file(tmp_path, body))
    assert status == "CONFORMANT"
    assert any(r["note"] == "duplicate_adjacent_line" for r in rows)


def test_fenced_pipe_rows_are_ignored_by_guards(tmp_path):
    body = (
        FOLD_HEADER
        + "| f1 | 1 | ACID | 5.1 | pre-existing | a | ADDITION | kept |\n\n"
        + "```\n| x | x | x | x | x | x | x | x |\n| x | x | x | x | x | x | x | x |\n```\n"
    )
    status, rows, _ = validate_file(_v03_file(tmp_path, body))
    assert status == "CONFORMANT"
    assert not any(r["note"] in ("headerless_rows", "duplicate_row") for r in rows)


def test_fully_detached_rows_no_table_still_flagged(tmp_path):
    body = (
        "prose only, no table header anywhere\n\n"
        "| f1 | 1 | ACID | 5.1 | pre-existing | detached | ADDITION | kept |\n"
    )
    status, rows, _ = validate_file(_v03_file(tmp_path, body))
    assert status == "UNCONFORMANT"
    assert any(r["note"] == "headerless_rows" for r in rows)


# ---- version-aware classification (register-enforcement-2026-09-03) ----


def test_legacy_schema_v01_not_no_table(tmp_path):
    """Test 1 — a register declaring schema_version 0.1 (below validator v0.3) must
    not be reported as NO_TABLE. It gets its own legacy status and is not a defect."""
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        **schema_version:** `0.1`

        | # | measurement | result |
        |---|---|---|
        | 1 | count | ok |
        """)
    status, rows, shapes = validate_file(p)
    assert status == STATUS_LEGACY_SCHEMA, f"expected LEGACY_SCHEMA, got {status!r}"
    assert status != STATUS_NO_TABLE


def test_future_schema_unjudgeable(tmp_path):
    """Test 1b — a register declaring a version ABOVE the validator's own (0.3) is
    unjudgeable; the validator is too old to assess it. Reported as FUTURE_SCHEMA.

    CONSTRUCTED FIXTURE: no register in the corpus declares >0.3 as of 2026-09-03.
    This arm is built for a case that cannot yet occur in the wild.
    """
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        **schema_version:** `0.4`

        | id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
        |---|---|---|---|---|---|---|---|
        | f1 | 1 | Weak spots | 1.1 | pre-existing | something | bytes | fixed |
        """)
    status, rows, shapes = validate_file(p)
    assert status == STATUS_FUTURE_SCHEMA, f"expected FUTURE_SCHEMA, got {status!r}"


def test_v03_no_fold_table_is_no_table(tmp_path):
    """Test 2 — a register declaring v0.3 (current) with no fold table → NO_TABLE.
    Verifies that the version-aware branch preserves existing NO_TABLE behavior
    for current-schema registers without fold tables."""
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        **schema_version:** `0.3`

        No fold tables here.
        """)
    status, rows, shapes = validate_file(p)
    assert status == STATUS_NO_TABLE


def test_no_declaration_still_pre_schema_regression(tmp_path):
    """Test 3 (regression) — a register with no schema_version declaration stays
    PRE-SCHEMA after the version-aware change. PRE-SCHEMA is not a defect."""
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        No schema_version declaration.

        | # | finding | fold |
        |---|---|---|
        | 1 | bad count | fixed |
        """)
    status, rows, shapes = validate_file(p)
    assert status == STATUS_PRE_SCHEMA


# ---- validate-first / exempt-second (plan 100030, 2026-09-03) ----


def test_v01_conformant_fold_table_stays_conformant(tmp_path):
    """Test 1 — a v0.1 register whose fold table IS v0.3-conformant → CONFORMANT with rows.
    The regression 100029 introduced: a conformant register must not be exempted."""
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        **schema_version:** `0.1`

        | id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
        |---|---|---|---|---|---|---|---|
        | f1 | 1 | Weak spots | 1.1 | pre-existing | bad count | the bytes | fixed |
        """)
    status, rows, shapes = validate_file(p)
    assert status == STATUS_CONFORMANT, f"expected CONFORMANT, got {status!r}"
    assert len(rows) > 0, "rows must be non-empty for a conformant register"


def test_v01_wrong_shaped_fold_table_is_legacy_with_rows(tmp_path):
    """Test 2 — a v0.1 register with a wrong-shaped fold table → LEGACY_SCHEMA with rows.
    An old declaration explains a failure; it does not excuse a passing register."""
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        **schema_version:** `0.1`

        | # | finding | fold |
        |---|---|---|
        | 1 | bad count | fixed |
        """)
    status, rows, shapes = validate_file(p)
    assert status == STATUS_LEGACY_SCHEMA, f"expected LEGACY_SCHEMA, got {status!r}"
    assert len(rows) > 0, "rows must be non-empty even for LEGACY_SCHEMA"


def test_v01_no_fold_table_is_legacy_not_no_table(tmp_path):
    """Test 3 — a v0.1 register with no fold table at all → LEGACY_SCHEMA, not NO_TABLE."""
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        **schema_version:** `0.1`

        Just prose. No tables at all.
        """)
    status, rows, shapes = validate_file(p)
    assert status == STATUS_LEGACY_SCHEMA, f"expected LEGACY_SCHEMA, got {status!r}"
    assert status != STATUS_NO_TABLE


def test_future_schema_rows_still_emitted(tmp_path):
    """Test 4 — a FUTURE version register whose fold table conforms → FUTURE_SCHEMA with rows.
    Status flags unjudgeability; rows must never be discarded."""
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        **schema_version:** `0.4`

        | id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
        |---|---|---|---|---|---|---|---|
        | f1 | 1 | Weak spots | 1.1 | pre-existing | bad count | the bytes | fixed |
        """)
    status, rows, shapes = validate_file(p)
    assert status == STATUS_FUTURE_SCHEMA, f"expected FUTURE_SCHEMA, got {status!r}"
    assert len(rows) > 0, "rows must be non-empty even for FUTURE_SCHEMA"


def test_pre_schema_unchanged_post_version_fix(tmp_path):
    """Test 5 — PRE-SCHEMA (no declaration) is unchanged by the validate-first fix."""
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        No schema_version declaration.

        | # | finding | fold |
        |---|---|---|
        | 1 | bad count | fixed |
        """)
    status, rows, shapes = validate_file(p)
    assert status == STATUS_PRE_SCHEMA


def test_v03_conformant_positive_control(tmp_path):
    """Test 6 — a conformant v0.3 register is unaffected by the validate-first change."""
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        **schema_version:** `0.3`

        | id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |
        |---|---|---|---|---|---|---|---|
        | f1 | 1 | Weak spots | 1.1 | pre-existing | bad count | the bytes | fixed |
        """)
    status, rows, shapes = validate_file(p)
    assert status == STATUS_CONFORMANT
    assert len(rows) == 1


def test_rows_never_empty_on_exemption_path(tmp_path):
    """Test 7 — ⛔ rows must never be empty on the exemption path.
    A v0.1 register with parseable fold rows emits them regardless of final status."""
    p = _write_register(tmp_path, "walk-register-test.md", """\
        # Walk Register — test

        **schema_version:** `0.1`

        | # | finding | fold |
        |---|---|---|
        | 1 | bad count | fixed |
        | 2 | stale ref | new ref |
        """)
    status, rows, shapes = validate_file(p)
    assert status in (STATUS_LEGACY_SCHEMA, STATUS_CONFORMANT), f"unexpected status {status!r}"
    assert len(rows) >= 2, "rows must never be empty on the exemption path"
