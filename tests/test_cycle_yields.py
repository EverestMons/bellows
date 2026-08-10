"""Hermetic tests for the cycle yields collector.

Every case uses inline fixture strings or tmp_path — no test reads the live corpus.
"""

import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

from cycle_yields import (
    COLUMNS,
    ORIGIN_ABSENT,
    ORIGIN_NA,
    ORIGIN_PARTIAL,
    ORIGIN_PRESENT,
    STATUS_MULTIPLE_BLOCKS,
    STATUS_NO_BLOCK,
    STATUS_OK,
    STATUS_UNPARSEABLE,
    collect,
    extract_dc_blocks,
    extract_passes,
    extract_plan_id,
    find_root,
    parse_lens_line,
    parse_origin,
)


def _build_shop(tmp_path, files):
    """Build a miniature shop under tmp_path with DRAFTING_CYCLE.md marker."""
    (tmp_path / "DRAFTING_CYCLE.md").write_text("marker", encoding="utf-8")
    done = tmp_path / "project" / "knowledge" / "decisions" / "Done"
    done.mkdir(parents=True)
    for name, content in files.items():
        (done / name).write_text(content, encoding="utf-8")
    return tmp_path


# --- (a) v2.0 line WITH origin split → PRESENT ---


def test_origin_present():
    line = "- Weak spots:          w1 6 folded (6 / 0); w2 3 folded (1 / 2)."
    parsed = parse_lens_line(line)
    assert parsed is not None
    assert len(parsed) == 2
    lens, tok, fld, pe, fi, orig = parsed[0]
    assert lens == "weak-spots"
    assert tok == "w1"
    assert fld == "6"
    assert pe == "6"
    assert fi == "0"
    assert orig == ORIGIN_PRESENT
    _, _, _, pe2, fi2, orig2 = parsed[1]
    assert pe2 == "1"
    assert fi2 == "2"
    assert orig2 == ORIGIN_PRESENT


# --- (b) pre-v2.0 line WITHOUT origin split → ABSENT, never 0 ---


def test_origin_absent_not_zero():
    line = "- Weak spots: w1 5 folded; w2 1 folded."
    parsed = parse_lens_line(line)
    assert parsed is not None
    for item in parsed:
        _, _, _, pe, fi, orig = item
        assert orig == ORIGIN_ABSENT
        assert pe == "-", "pre_existing must be '-', not '0'"
        assert fi == "-", "fold_introduced must be '-', not '0'"


# --- (c) malformed line → UNPARSEABLE, row still emitted ---


def test_unparseable_emitted():
    line = "- Weak spots: w1 several folded, see register."
    parsed = parse_lens_line(line)
    assert parsed is not None
    assert len(parsed) >= 1
    assert parsed[0][0] == "UNPARSEABLE"


# --- (d) no block → NO_BLOCK ---


def test_no_block(tmp_path):
    shop = _build_shop(tmp_path, {
        "executable-270.md": "# Some plan\n\nNo cycle block here.\n",
    })
    rows, disc, blk = collect(shop)
    assert disc == 1
    assert blk == 0
    assert len(rows) == 1
    fields = rows[0].split("\t")
    assert fields[COLUMNS.index("status")] == STATUS_NO_BLOCK
    assert fields[COLUMNS.index("origin")] == ORIGIN_NA


# --- (e) two ## Drafting Cycle headings → MULTIPLE_BLOCKS ---


def test_multiple_blocks(tmp_path):
    content = (
        "# Plan\n\n"
        "## Drafting Cycle\n\n"
        "- Weak spots: w1 5 folded.\n\n"
        "## Other section\n\n"
        "## Drafting Cycle\n\n"
        "- Weak spots: w1 2 folded.\n\n"
        "## End\n"
    )
    shop = _build_shop(tmp_path, {"executable-330.md": content})
    rows, disc, blk = collect(shop)
    assert disc == 1
    assert blk == 1
    assert len(rows) == 2
    for row in rows:
        fields = row.split("\t")
        assert fields[COLUMNS.index("status")] == STATUS_MULTIPLE_BLOCKS
    blocks = [row.split("\t")[COLUMNS.index("block")] for row in rows]
    assert blocks == ["1", "2"]


# --- (f) All lenses form → parsed ---


def test_all_lenses_parsed():
    line = "- All lenses, w4: 1 folded."
    parsed = parse_lens_line(line)
    assert parsed is not None
    assert len(parsed) == 1
    lens, tok, fld, pe, fi, orig = parsed[0]
    assert lens == "all-lenses"
    assert tok == "w4"
    assert fld == "1"


def test_all_lenses_dry():
    line = "- All lenses, w5 (final confirming, whole artifact): DRY — zero findings."
    parsed = parse_lens_line(line)
    assert parsed is not None
    lens, tok, fld, _, _, _ = parsed[0]
    assert lens == "all-lenses"
    assert tok == "w5"
    assert fld == "0"


def test_all_lenses_with_description():
    line = "- All lenses, w3 (confirming, ROTATED to regions walks 1-2 never touched): 2 folded, both minor."
    parsed = parse_lens_line(line)
    assert parsed is not None
    lens, tok, fld, _, _, _ = parsed[0]
    assert lens == "all-lenses"
    assert tok == "w3"
    assert fld == "2"


# --- (g) empty block → zero rows, no crash ---


def test_empty_block(tmp_path):
    content = "# Plan\n\n## Drafting Cycle\n\n## End\n"
    shop = _build_shop(tmp_path, {"executable-999.md": content})
    rows, disc, blk = collect(shop)
    assert disc == 1
    assert blk == 1
    assert len(rows) == 0


# --- (h) heading inside fence → not counted as a block ---


def test_heading_in_fence_not_counted():
    text = (
        "# Plan\n\n"
        "```\n## Drafting Cycle\n```\n\n"
        "## Real section\n"
    )
    blocks = extract_dc_blocks(text)
    assert len(blocks) == 0


# --- (i) column-count invariant ---


def test_column_count_invariant(tmp_path):
    content_ok = (
        "# Plan\n\n## Drafting Cycle\n\n"
        "- Weak spots: w1 3 folded (2 / 1).\n\n## End\n"
    )
    content_no_block = "# Plan\n\nNo block.\n"
    content_unparseable = (
        "# Plan\n\n## Drafting Cycle\n\n"
        "- Weak spots: w1 several folded.\n\n## End\n"
    )
    shop = _build_shop(tmp_path, {
        "executable-100.md": content_ok,
        "executable-200.md": content_no_block,
        "executable-300.md": content_unparseable,
    })
    rows, _, _ = collect(shop)
    expected = len(COLUMNS)
    for row in rows:
        fields = row.split("\t")
        assert len(fields) == expected, f"Row has {len(fields)} fields, expected {expected}: {row}"


# --- (j) one real heading + one in fence → OK with block=1 ---


def test_real_plus_fenced_heading():
    text = (
        "# Plan\n\n"
        "```\n## Drafting Cycle\n```\n\n"
        "## Drafting Cycle\n\n"
        "- Weak spots: w1 2 folded.\n\n## End\n"
    )
    blocks = extract_dc_blocks(text)
    assert len(blocks) == 1


def test_real_plus_fenced_ok_status(tmp_path):
    content = (
        "# Plan\n\n"
        "```\n## Drafting Cycle\n```\n\n"
        "## Drafting Cycle\n\n"
        "- Weak spots: w1 2 folded.\n\n## End\n"
    )
    shop = _build_shop(tmp_path, {"executable-400.md": content})
    rows, _, _ = collect(shop)
    assert len(rows) == 1
    fields = rows[0].split("\t")
    assert fields[COLUMNS.index("status")] == STATUS_OK
    assert fields[COLUMNS.index("block")] == "1"


# --- (k) multi-pass lens line → THREE rows ---


def test_multi_pass_three_rows():
    line = "- Weak spots: w1 2 folded; w2 dry; w3 dry."
    parsed = parse_lens_line(line)
    assert parsed is not None
    assert len(parsed) == 3
    tokens = [p[1] for p in parsed]
    assert tokens == ["w1", "w2", "w3"]


# --- (l) dry pass → folded=0 ---


def test_dry_pass_zero():
    line = "- Destruction: w1 1 folded; w2 dry."
    parsed = parse_lens_line(line)
    assert parsed is not None
    dry_pass = [p for p in parsed if p[1] == "w2"]
    assert len(dry_pass) == 1
    _, _, fld, _, _, _ = dry_pass[0]
    assert fld == "0"


# --- (m) half-split → PARTIAL ---


def test_half_split_partial():
    line = "- Weak spots: w1 6 folded (6 pre-existing)."
    parsed = parse_lens_line(line)
    assert parsed is not None
    lens, tok, fld, pe, fi, orig = parsed[0]
    assert orig == ORIGIN_PARTIAL
    assert pe == "6"
    assert fi == "-"


def test_half_split_fold_introduced():
    line = "- ACID: a1 4 folded (4 fold-introduced)."
    parsed = parse_lens_line(line)
    assert parsed is not None
    _, _, _, pe, fi, orig = parsed[0]
    assert orig == ORIGIN_PARTIAL
    assert pe == "-"
    assert fi == "4"


# --- Additional edge cases ---


def test_plan_id_extraction():
    assert extract_plan_id("executable-332.md") == "332"
    assert extract_plan_id("diagnostic-311.md") == "311"
    assert extract_plan_id("halted-executable-334.md") == "334"
    assert extract_plan_id("in-progress-executable-335.md") == "335"
    assert extract_plan_id("parallel-1-executable-forge-kb-integration-2026-03-24.md") == "-"
    assert extract_plan_id("roadmap-per-plan-tracker.md") == "-"
    assert extract_plan_id("diagnostic-planner-rule-violation-and-insertion-point-map-2026-05-07.md") == "-"


def test_find_root(tmp_path):
    (tmp_path / "DRAFTING_CYCLE.md").write_text("marker", encoding="utf-8")
    sub = tmp_path / "project" / "scripts"
    sub.mkdir(parents=True)
    found = find_root(sub)
    assert found == tmp_path


def test_find_root_not_found(tmp_path):
    found = find_root(tmp_path)
    assert found is None


def test_parse_origin_full():
    orig, pe, fi = parse_origin(" (3 / 2)")
    assert orig == ORIGIN_PRESENT
    assert pe == "3"
    assert fi == "2"


def test_parse_origin_absent():
    orig, pe, fi = parse_origin(" no split here")
    assert orig == ORIGIN_ABSENT
    assert pe == "-"
    assert fi == "-"


def test_acid_lens():
    line = "- ACID: a1 5 folded (2 / 3); a2 2 folded (0 / 2)."
    parsed = parse_lens_line(line)
    assert parsed is not None
    assert len(parsed) == 2
    assert parsed[0][0] == "acid"
    assert parsed[0][1] == "a1"
    assert parsed[1][1] == "a2"


def test_integration_record_lens():
    line = "- Integration-record: w1 2 folded."
    parsed = parse_lens_line(line)
    assert parsed is not None
    assert parsed[0][0] == "integration-record"


def test_confirming_close():
    line = "- Confirming close (cc, all five lenses over the panel-folded artifact): DRY"
    parsed = parse_lens_line(line)
    assert parsed is not None
    lens, tok, fld, _, _, _ = parsed[0]
    assert lens == "confirming-close"
    assert tok == "cc"
    assert fld == "0"


def test_source_column_always_record_claimed(tmp_path):
    content = (
        "# Plan\n\n## Drafting Cycle\n\n"
        "- Weak spots: w1 3 folded.\n\n## End\n"
    )
    shop = _build_shop(tmp_path, {"executable-500.md": content})
    rows, _, _ = collect(shop)
    for row in rows:
        fields = row.split("\t")
        assert fields[COLUMNS.index("source")] == "RECORD_CLAIMED"


def test_warning_bullet_skipped():
    line = "- ⚠️ This is a warning bullet, not a lens line."
    parsed = parse_lens_line(line)
    assert parsed is None


def test_non_bullet_line_skipped():
    line = "**Closing:** the last event is a lens pass."
    parsed = parse_lens_line(line)
    assert parsed is None


def test_discovery_counts(tmp_path):
    shop = _build_shop(tmp_path, {
        "executable-1.md": "# Plan\n\n## Drafting Cycle\n\n- Weak spots: w1 1 folded.\n",
        "executable-2.md": "# Plan\n\nNo block.\n",
        "not-a-plan.txt": "text file, not .md",
    })
    rows, disc, blk = collect(shop)
    assert disc == 2
    assert blk == 1


def test_encoding_utf8(tmp_path):
    content = (
        "# Plan\n\n## Drafting Cycle\n\n"
        "- Weak spots: w1 3 folded — ⚠️ note with unicode.\n\n## End\n"
    )
    shop = _build_shop(tmp_path, {"executable-600.md": content})
    rows, _, _ = collect(shop)
    assert len(rows) == 1


def test_dot_prefixed_dirs_skipped(tmp_path):
    shop = _build_shop(tmp_path, {})
    hidden = tmp_path / ".hidden" / "knowledge" / "decisions" / "Done"
    hidden.mkdir(parents=True)
    (hidden / "executable-700.md").write_text(
        "# Plan\n\n## Drafting Cycle\n\n- Weak spots: w1 1 folded.\n",
        encoding="utf-8",
    )
    rows, disc, _ = collect(shop)
    assert disc == 0


def test_pass_with_parenthetical_qualifier():
    line = "- Weak spots: w1 2 folded; w2 1 folded; **w3 (confirming) 2 folded — NOT dry**: description."
    parsed = parse_lens_line(line)
    assert parsed is not None
    tokens = [p[1] for p in parsed]
    assert "w1" in tokens
    assert "w2" in tokens
    assert "w3" in tokens
