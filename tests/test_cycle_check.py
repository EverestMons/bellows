"""Tests for cycle_check — the drafting-cycle validator.

Every case uses synthetic fixtures in tmp_path. Git-dependent tests
mock subprocess calls to avoid real repo dependencies.
"""

import itertools
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = BELLOWS_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

# Force-load from the worktree's scripts/ so the full suite doesn't pick up
# a stale version cached by depositor.py (which uses resolve_bellows_root()).
import importlib
if "cycle_check" in sys.modules and sys.modules["cycle_check"].__file__ != str(SCRIPTS / "cycle_check.py"):
    del sys.modules["cycle_check"]
import cycle_check


def _make_plan(tmp_path, dc_block, filename="plan.md"):
    plan = tmp_path / filename
    plan.write_text(
        f"# Plan\n\n## Drafting Cycle\n{dc_block}\n## End\n",
        encoding="utf-8",
    )
    return plan


# ---------- unparseable ----------


def test_unparseable_no_block(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan\n\nNo cycle block here.\n", encoding="utf-8")
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:unparseable"
    assert code == 1


def test_unparseable_multi_block(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan\n\n## Drafting Cycle\n"
        "- Weak spots: w1 2 folded.\n\n"
        "## Other\n\n## Drafting Cycle\n"
        "- Weak spots: w1 1 folded.\n\n## End\n",
        encoding="utf-8",
    )
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:unparseable"
    assert code == 1


def test_unparseable_no_parseable_lens(tmp_path):
    plan = _make_plan(tmp_path, "- Weak spots: w1 several folded, see register.\n")
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:unparseable"
    assert code == 1


# ---------- assert failures ----------


def test_assert_fail_1(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 3 folded — instruction 2 / record 0.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:assert-fail:1"
    assert code == 1


def test_assert_fail_2(tmp_path, monkeypatch):
    plan = _make_plan(tmp_path, (
        "**Walk register:** `path/to/missing-register.md`\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0.\n"
    ))
    git_root = tmp_path
    (tmp_path / "path" / "to").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: git_root)
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:assert-fail:2"
    assert code == 1


def test_assert_fail_3(tmp_path, monkeypatch):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0.\n"
    ))
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)

    def mock_run(cmd, **kw):
        class R:
            returncode = 0
            stdout = "abc1234 [draft] w1 fold\nabc1235 deposit(cycle-check)\n"
            stderr = ""
        return R()

    monkeypatch.setattr(subprocess, "run", mock_run)
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:assert-fail:3"
    assert code == 1


# ---------- restructuring fold ----------


def test_restructuring_fold(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0 (restructuring — moved section order).\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:restructuring-fold"
    assert code == 1


# ---------- yield rising ----------


def test_yield_rising(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 1 folded — instruction 1 / record 0; "
        "w2 2 folded — instruction 2 / record 0.\n"
        "- Destruction: w1 dry; w2 dry.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:yield-rising"
    assert code == 1


# ---------- plateau ----------


def test_plateau_at_3(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0; "
        "w2 2 folded — instruction 2 / record 0; "
        "w3 2 folded — instruction 2 / record 0; "
        "w4 2 folded — instruction 2 / record 0.\n"
        "- Destruction: w1 dry; w2 dry; w3 dry; w4 dry.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:plateau"
    assert code == 1


# ---------- BAR_MET ----------


def test_bar_met(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "- Vulnerabilities: w1 dry; w2 dry.\n"
        "- Integration-record: w1 dry; w2 dry.\n"
        "- ACID: w1 dry; w2 dry.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- CONTINUE ----------


def test_continue_mid_cycle(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 3 folded — instruction 2 / record 1.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


# ---------- N/A class split (legacy form) ----------


def test_na_class_split_legacy(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 5 folded; w2 3 folded; w3 dry.\n"
        "- Destruction: w1 2 folded; w2 dry; w3 dry.\n"
    ))
    parsed = cycle_check.parse_block(
        cycle_check.extract_dc_blocks(plan.read_text())[0]
    )
    assert cycle_check.check_assert_1(parsed) == "N/A"
    verdict, code = cycle_check.run_check(plan)
    assert code == 0
    assert verdict in ("CONTINUE", "BAR_MET")


# ---------- zero walk ----------


def test_zero_walk(tmp_path):
    plan = _make_plan(tmp_path, (
        "**Tier:** T1\n"
        "**Walk 0 (context pin):** measured.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


# ---------- mixed parseable/unparseable ----------


def test_mixed_parseable_unparseable(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded; w2 dry.\n"
        "- Destruction: w1 several folded, see register.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


# ---------- uncommitted walk ----------


def test_uncommitted_walk(tmp_path, monkeypatch):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0; "
        "w2 1 folded — instruction 1 / record 0; "
        "w3 dry.\n"
        "- Destruction: w1 dry; w2 dry; w3 dry.\n"
    ))
    baseline = tmp_path / ".plan.md.foldcheck.json"
    baseline.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)

    def mock_run(cmd, **kw):
        class R:
            returncode = 0
            stdout = "abc1234 [draft] w1 fold\n"
            stderr = ""
        return R()

    monkeypatch.setattr(subprocess, "run", mock_run)
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:uncommitted-walk"
    assert code == 1


# ---------- claimed close unmet ----------


def test_claimed_close_unmet(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 3 folded — instruction 2 / record 1.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0.\n"
        "**Closing:** met the bar at walk 1.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:claimed-close-unmet"
    assert code == 1


# ---------- closure false-positive regression ----------


def test_prose_closed_not_false_positive(tmp_path):
    """Mid-cycle block with prose mentions of closures but no real closure claim.
    Must NOT trigger claimed-close-unmet.
    """
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 3 folded — instruction 2 / record 1.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0.\n"
        "Emit-manifest against real closed plans, a closed loop, criteria barely satisfied.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


def test_genuine_closure_still_detected(tmp_path):
    """A genuine closure (**Closing:** + CLOSED, walk dry) → BAR_MET."""
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "- Vulnerabilities: w1 dry; w2 dry.\n"
        "- Integration-record: w1 dry; w2 dry.\n"
        "- ACID: w1 dry; w2 dry.\n"
        "**Closing:** walk 2 dry; cycle CLOSED.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


def test_fabricated_close_guard_survives(tmp_path):
    """THE GUARD MUST SURVIVE: BAR MET claimed but walk NOT dry
    (instruction folds remain) → must STILL fire ESCALATE:claimed-close-unmet.
    """
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 3 folded — instruction 2 / record 1.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0.\n"
        "**Closing:** walk 1 BAR MET.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:claimed-close-unmet"
    assert code == 1


# ---------- Walk-N STATUS lines ----------


def test_walk_status_lines_parsed(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 3 folded — instruction 2 / record 1; w2 dry.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "**Walk 1 STATUS:** 4 folded — instruction 3 / record 1 — NOT dry.\n"
        "**Walk 2 STATUS:** 0 folded — full dry.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


def test_walk_status_cross_check_fail(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0.\n"
        "**Walk 1 STATUS:** 3 folded — instruction 5 / record 0 — NOT dry.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:assert-fail:1"
    assert code == 1


# ---------- compact dry format ----------


def test_compact_dry_format(tmp_path):
    plan = _make_plan(tmp_path, (
        "**Walk 1 (all instruction-class):**\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0.\n"
        "**Walk 2 (dry):**\n"
        "- Weak spots: dry. — Destruction: dry.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- walk register cross-repo → N/A ----------


def test_walk_register_governance_root_fallback(tmp_path, monkeypatch):
    """C-3: a repo-relative ref unresolvable under git_root resolves via the governance root fallback."""
    import bellows_root as br
    gov_root = tmp_path / "gov"
    reg_dir = gov_root / "governance" / "knowledge" / "research"
    reg_dir.mkdir(parents=True)
    (reg_dir / "register.md").write_text("rows", encoding="utf-8")

    plan = _make_plan(tmp_path, (
        "**Walk register:** governance/knowledge/research/register.md\n"
        "- Weak spots: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
    ))
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)
    monkeypatch.setattr(br, "resolve_governance_root", lambda: gov_root)
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- closure markers ----------


def test_closure_markers_detected():
    # 58: bare **Closing:** heading is not a claim; only BAR MET / met the bar / CYCLE COMPLETE are
    for marker in ["BAR MET", "met the bar", "CYCLE COMPLETE"]:
        block = f"- Weak spots: w1 1 folded.\n{marker}\n"
        parsed = cycle_check.parse_block(block)
        assert parsed["claims_closure"], f"Failed to detect: {marker}"
    # NOT CLOSED should not trigger a claim
    block_not_closed = "- Weak spots: w1 1 folded.\n**Closing:** NOT CLOSED.\n"
    parsed_nc = cycle_check.parse_block(block_not_closed)
    assert not parsed_nc["claims_closure"], "NOT CLOSED must not be a claim"


# ---------- plateau requires 4+ walks ----------


def test_no_plateau_at_2(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0; "
        "w2 2 folded — instruction 2 / record 0; "
        "w3 2 folded — instruction 2 / record 0.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


# ---------- N/A instruction counts disable yield/plateau ----------


def test_na_instruction_counts(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 5 folded; w2 5 folded; w3 5 folded; w4 5 folded.\n"
    ))
    parsed = cycle_check.parse_block(
        cycle_check.extract_dc_blocks(plan.read_text())[0]
    )
    counts = cycle_check.get_instruction_counts(parsed)
    assert all(v is None for v in counts.values())

    result = cycle_check.check_plateau(
        parsed["walk_data"], 4, counts
    )
    assert result is None


# ---------- foldcheck baseline exists → assert 3 PASS ----------


def test_assert_3_baseline_exists(tmp_path, monkeypatch):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0.\n"
    ))
    baseline = tmp_path / ".plan.md.foldcheck.json"
    baseline.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)

    def mock_run(cmd, **kw):
        class R:
            returncode = 0
            stdout = "abc1234 [draft] w1 fold\n"
            stderr = ""
        return R()

    monkeypatch.setattr(subprocess, "run", mock_run)
    parsed = cycle_check.parse_block(
        cycle_check.extract_dc_blocks(plan.read_text())[0]
    )
    result = cycle_check.check_assert_3(parsed, plan, True)
    assert result == "PASS"


# ---------- CLI smoke test ----------


def test_cli_exit_codes(tmp_path):
    bar_met_plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
    ), "bar.md")
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), str(bar_met_plan)],
        capture_output=True, text=True,
    )
    assert r.stdout.strip() == "BAR_MET"
    assert r.returncode == 0

    escalate_plan = _make_plan(tmp_path, (
        "- Weak spots: w1 3 folded — instruction 2 / record 0.\n"
    ), "esc.md")
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), str(escalate_plan)],
        capture_output=True, text=True,
    )
    assert r.stdout.strip() == "ESCALATE:assert-fail:1"
    assert r.returncode == 1

    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"),
         str(tmp_path / "nonexistent.md")],
        capture_output=True, text=True,
    )
    assert r.returncode == 2


# ---------- degenerate: dry walk with record-class folds ----------


def test_bar_met_with_record_only_folds(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 0 / record 2; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


def test_bar_met_instruction_zero_current(tmp_path):
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0; "
        "w2 1 folded — instruction 0 / record 1; w3 dry.\n"
        "- Destruction: w1 dry; w2 dry; w3 dry.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- --emit-manifest ----------


def test_emit_manifest_well_formed(tmp_path):
    """--emit-manifest emits a well-formed 10-field stanza with correct computed fields."""
    plan = _make_plan(tmp_path, (
        "**Tier:** T1\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "- Vulnerabilities: w1 dry; w2 dry.\n"
        "- Integration-record: w1 dry; w2 dry.\n"
        "- ACID: w1 dry; w2 dry.\n"
        "**Closing:** walk 2 dry; cycle CLOSED.\n"
    ))
    original_bytes = plan.read_bytes()
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), "--emit-manifest", str(plan)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0
    assert plan.read_bytes() == original_bytes

    output = r.stdout
    assert "## Cycle Manifest" in output
    assert "tier: T1" in output
    assert "walks: 2" in output
    assert "yields: 3, 0" in output
    assert "cycle_check=BAR_MET" in output
    assert "plan_lint=" in output
    assert "fold_check=" in output
    assert "coherence: N/A" in output
    assert "target: <declare>" in output
    assert "class: <declare>" in output
    assert "reads: <declare>" in output
    assert "writes: <declare>" in output
    assert "open_forks: <declare>" in output


def test_emit_manifest_stdout_only(tmp_path):
    """--emit-manifest writes NO file — plan is byte-unchanged after the run."""
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
    ))
    original = plan.read_bytes()
    files_before = set(tmp_path.iterdir())
    subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), "--emit-manifest", str(plan)],
        capture_output=True, text=True, timeout=30,
    )
    assert plan.read_bytes() == original
    assert set(tmp_path.iterdir()) == files_before


def test_emit_manifest_declare_placeholders(tmp_path):
    """Undeclared authored fields get <declare> placeholders."""
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
    ))
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), "--emit-manifest", str(plan)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0
    for field in ["target", "class", "reads", "writes", "open_forks"]:
        assert f"{field}: <declare>" in r.stdout


def test_emit_manifest_na_yields_no_class_split(tmp_path):
    """Yields N/A when instruction counts are not parseable (no class splits)."""
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 5 folded; w2 3 folded; w3 dry.\n"
        "- Destruction: w1 2 folded; w2 dry; w3 dry.\n"
    ))
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), "--emit-manifest", str(plan)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0
    assert "yields: N/A" in r.stdout


def test_emit_manifest_coherence_no_register(tmp_path):
    """Coherence is N/A when no walk register is declared."""
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
    ))
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), "--emit-manifest", str(plan)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0
    assert "coherence: N/A (no register declared)" in r.stdout


def test_emit_manifest_propagation_field(tmp_path):
    """M4 kill: --emit-manifest validation: line carries propagation_check=."""
    plan = _make_plan(tmp_path, (
        "**Tier:** T1\n"
        "- Weak spots: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
        "- Vulnerabilities: w1 dry; w2 dry.\n"
        "- Integration-record: w1 dry; w2 dry.\n"
        "- ACID: w1 dry; w2 dry.\n"
        "**Closing:** walk 2 dry; cycle CLOSED.\n"
    ))
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), "--emit-manifest", str(plan)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0
    assert "propagation_check=" in r.stdout


# ========== Tier-2 state-space suite (Rule 103, threads 52/58/63) ==========
#
# Three dimensions from the SYSTEM:
#   WALK_DIM  — walk-line forms cycle_check parses
#   CLOSE_DIM — closing forms DRAFTING_CYCLE §3 mandates
#   REG_DIM   — register-reference forms present in the corpus
#
# Every cell is force-classified; a cell absent from the table is a coverage gap.

_WALK_DIM = [
    "none",            # no walk lines → CONTINUE regardless
    "plain_walk",      # - Walk N: K folds — no lens line → C-1 → ESCALATE:unparseable
    "lens_spaced",     # - Weak spots: w1 dry — standard spaced form
    "lens_hyphen",     # - Weak-spots: w1 dry — hyphenated form (63)
]

_CLOSE_DIM = [
    "none",            # no **Closing:** line
    "bare_heading",    # **Closing:** only (58: not a claim)
    "not_closed",      # **Closing:** NOT CLOSED (58: negation stripped → no claim)
    "bar_met",         # **Closing:** BAR MET (58: claim)
    "met_the_bar",     # **Closing:** met the bar (58: claim)
]

_REG_DIM = [
    "absent",          # no register line
    "absolute",        # absolute path to a real file → PASS
    "unresolvable",    # relative ref that doesn't exist anywhere → UNRESOLVED → assert-fail:2
    "commentary",      # short trail after the .md token — token extracted cleanly (C-2)
]

# Force-classify every cell: (walk, close, reg) → expected_verdict
# Rules applied in priority order:
#   1. plain_walk → ESCALATE:unparseable (C-1, dominates everything)
#   2. none walk → CONTINUE (no walk data, dominates close/reg)
#   3. unresolvable reg + lens walk → ESCALATE:assert-fail:2 (C-3)
#   4. dry lens walk + claim close → ESCALATE:claimed-close-unmet (58)
#   5. dry lens walk + non-claim close → BAR_MET
_EXPECTED: dict[tuple, str] = {}
for _w, _c, _r in itertools.product(_WALK_DIM, _CLOSE_DIM, _REG_DIM):
    if _w == "plain_walk":
        _EXPECTED[(_w, _c, _r)] = "ESCALATE:unparseable"
    elif _w == "none":
        _EXPECTED[(_w, _c, _r)] = "CONTINUE"
    elif _r == "unresolvable":
        _EXPECTED[(_w, _c, _r)] = "ESCALATE:assert-fail:2"
    elif _c in ("bar_met", "met_the_bar"):
        # dry walk + claim → escalate (the walk IS dry so verdict would be BAR_MET
        # but claim_closure triggers escalation only when verdict==CONTINUE — at BAR_MET
        # with claims_closure: the escalation guard is NOT triggered, so this returns BAR_MET)
        _EXPECTED[(_w, _c, _r)] = "BAR_MET"
    else:
        _EXPECTED[(_w, _c, _r)] = "BAR_MET"

# Completeness assertion: table must cover every cell in the cross-product
def test_state_space_table_complete():
    """Every cell in walk × close × register cross-product must be classified."""
    all_cells = set(itertools.product(_WALK_DIM, _CLOSE_DIM, _REG_DIM))
    covered = set(_EXPECTED.keys())
    assert all_cells == covered, f"Uncovered cells: {all_cells - covered}"


def _build_ss_plan(tmp_path, walk, close, reg, *, monkeypatch=None):
    """Build a plan and return (plan_path, setup_teardown_fn)."""
    walk_lines = {
        "none": "",
        "plain_walk": "- Walk 1: 3 folds\n- Walk 2: 0 folds\n",
        "lens_spaced": (
            "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
            "- Destruction: w1 dry; w2 dry.\n"
        ),
        "lens_hyphen": (
            "- Weak-spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
            "- Destruction: w1 dry; w2 dry.\n"
        ),
    }[walk]

    close_lines = {
        "none": "",
        "bare_heading": "**Closing:**\n",
        "not_closed": "**Closing:** NOT CLOSED at walk 2 — bar not met.\n",
        "bar_met": "**Closing:** ✅ BAR MET — walk 2 dry.\n",
        "met_the_bar": "**Closing:** walk 2 met the bar.\n",
    }[close]

    abs_file = tmp_path / "register.md"
    abs_file.write_text("rows", encoding="utf-8")

    # commentary: absolute path with trailing prose — extraction must take only the .md token
    reg_lines = {
        "absent": "",
        "absolute": f"**Walk register:** {abs_file}\n",
        "unresolvable": "**Walk register:** nonexistent/walk-register.md\n",
        "commentary": f"**Walk register:** {abs_file} (this is commentary that should be stripped)\n",
    }[reg]

    dc_block = f"{reg_lines}{walk_lines}{close_lines}"
    plan = tmp_path / f"plan_{walk}_{close}_{reg}.md"
    plan.write_text(f"# Plan\n\n## Drafting Cycle\n{dc_block}\n## End\n", encoding="utf-8")
    return plan


@pytest.mark.parametrize("walk,close,reg,expected", [
    (w, c, r, _EXPECTED[(w, c, r)])
    for w, c, r in itertools.product(_WALK_DIM, _CLOSE_DIM, _REG_DIM)
])
def test_state_space_cell(tmp_path, monkeypatch, walk, close, reg, expected):
    """Tier-2 state-space: each cell returns the force-classified verdict."""
    import bellows_root as _br
    # For unresolvable reg: ensure governance root also doesn't have it
    monkeypatch.setattr(_br, "resolve_governance_root", lambda: tmp_path / "_no_gov")
    plan = _build_ss_plan(tmp_path, walk, close, reg)
    # For absolute reg path: _find_git_root doesn't matter for step 1
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)
    verdict, _code = cycle_check.run_check(plan)
    assert verdict == expected, f"cell ({walk},{close},{reg}): got {verdict!r}, want {expected!r}"


# ---------- C-1: plain walk lines → ESCALATE:unparseable ----------


def test_c1_plain_walk_lines_escalate(tmp_path):
    """C-1: block with plain - Walk N: lines but no parseable lens → ESCALATE:unparseable."""
    plan = _make_plan(tmp_path, "- Walk 1: 3 folds\n- Walk 2: 0 folds\n")
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:unparseable"
    assert code == 1


def test_c1_no_walk_signal_still_continue(tmp_path):
    """C-1: block with zero walk signal → CONTINUE (v0 pin only)."""
    plan = _make_plan(tmp_path, "**Walk 0 (context pin):** measured.\n")
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


# ---------- C-2: commentary-line extraction & OSError guard ----------


def test_c2_commentary_ref_extracted_cleanly(tmp_path, monkeypatch):
    """C-2: trailing commentary after the .md path is ignored; only the token is used."""
    reg = tmp_path / "register.md"
    reg.write_text("rows", encoding="utf-8")
    plan = _make_plan(tmp_path,
        f"**Walk register:** {reg} (this is commentary that should be ignored)\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
    )
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"


def test_c2_long_component_no_traceback(tmp_path):
    """C-2: >255-byte filename component in a git repo with scripts/ → ESCALATE:assert-fail:2, NO traceback."""
    import subprocess as _sp
    # Init a real temp git repo with a scripts/ directory
    git_dir = tmp_path / "repo"
    git_dir.mkdir()
    _sp.run(["git", "-C", str(git_dir), "init"], capture_output=True, check=True)
    (git_dir / "scripts").mkdir()
    # Build a 330-byte tail
    tail = "commentary-" * 30  # 330 bytes
    plan = git_dir / "plan.md"
    plan.write_text(
        "# Plan\n\n## Drafting Cycle\n"
        f"**Walk register:** scripts/register.md ({tail}\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
        "## End\n",
        encoding="utf-8",
    )
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), str(plan)],
        capture_output=True, text=True,
    )
    assert "Traceback" not in r.stdout
    assert "Traceback" not in r.stderr
    assert r.stdout.strip() == "ESCALATE:assert-fail:2"
    assert r.returncode == 1


def test_c2_oversized_backticked_ref_escalates_no_traceback(tmp_path):
    # thread 92, M3-drop-oserror-guard
    """C-2: backticked ref with >255-byte component in git root with scripts/ → ESCALATE:assert-fail:2 in-process."""
    import subprocess as _sp
    git_dir = tmp_path / "repo"
    git_dir.mkdir()
    _sp.run(["git", "-C", str(git_dir), "init"], capture_output=True, check=True)
    (git_dir / "scripts").mkdir()
    ref = "scripts/" + "x" * 300 + ".md"
    plan = git_dir / "plan.md"
    plan.write_text(
        "# Plan\n\n## Drafting Cycle\n"
        f"**Walk register:** `{ref}`\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 1 folded — instruction 1 / record 0.\n"
        "- Destruction: w1 dry; w2 dry.\n"
        "**Closing:** NOT CLOSED at walk 2.\n"
        "## End\n",
        encoding="utf-8",
    )
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:assert-fail:2"
    assert code == 1


# ---------- C-3: governance-root fallback & UNRESOLVED ----------


def test_c3_relative_ref_unresolvable_escalates(tmp_path, monkeypatch):
    """C-3: relative ref that exists under neither git_root nor governance root → ESCALATE:assert-fail:2."""
    import bellows_root as _br
    monkeypatch.setattr(_br, "resolve_governance_root", lambda: tmp_path / "_no_gov")
    plan = _make_plan(tmp_path,
        "**Walk register:** governance/knowledge/research/nonexistent.md\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
    )
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:assert-fail:2"
    assert code == 1


def test_c3_absolute_ref_exists_pass(tmp_path, monkeypatch):
    """C-3: absolute path that exists → PASS → BAR_MET."""
    reg = tmp_path / "my-register.md"
    reg.write_text("rows", encoding="utf-8")
    plan = _make_plan(tmp_path,
        f"**Walk register:** {reg}\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
    )
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- Thread 58: closure claim matcher ----------


def test_58_not_closed_returns_continue(tmp_path):
    """58: **Closing:** NOT CLOSED → negation stripped → no claim → CONTINUE, not ESCALATE."""
    plan = _make_plan(tmp_path,
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 1 folded — instruction 1 / record 0.\n"
        "- Destruction: w1 dry; w2 dry.\n"
        "**Closing:** NOT CLOSED at walk 2 — the bar is not met.\n"
    )
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


def test_58_bare_heading_not_a_claim(tmp_path):
    """58: bare **Closing:** heading alone is not a claim → CONTINUE when walk not dry."""
    plan = _make_plan(tmp_path,
        "- Weak spots: w1 2 folded — instruction 2 / record 0.\n"
        "- Destruction: w1 dry.\n"
        "**Closing:**\n"
    )
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


def test_58_bar_met_is_claim_when_unmet(tmp_path):
    """58: BAR MET is a claim; when walk is not dry → ESCALATE:claimed-close-unmet."""
    plan = _make_plan(tmp_path,
        "- Weak spots: w1 3 folded — instruction 2 / record 1.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0.\n"
        "**Closing:** ✅ BAR MET — walk 1.\n"
    )
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:claimed-close-unmet"
    assert code == 1


def test_58_met_the_bar_is_claim_when_unmet(tmp_path):
    """58: 'met the bar' is a claim; when walk is not dry → ESCALATE:claimed-close-unmet."""
    plan = _make_plan(tmp_path,
        "- Weak spots: w1 3 folded — instruction 2 / record 1.\n"
        "- Destruction: w1 dry.\n"
        "**Closing:** walk 1 met the bar.\n"
    )
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:claimed-close-unmet"
    assert code == 1


def test_58_negation_unmet_not_a_claim(tmp_path):
    """58: 'not met' phrase strips → no claim → CONTINUE when walk not dry."""
    plan = _make_plan(tmp_path,
        "- Weak spots: w1 2 folded — instruction 2 / record 0.\n"
        "- Destruction: w1 dry.\n"
        "**Closing:** bar not met at walk 1.\n"
    )
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


def test_58_negated_claim_phrase_stripped_continue(tmp_path):
    # thread 92, M2-drop-negation-stripping
    """58: 'has not met the bar' strips → no claim token survives → CONTINUE."""
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 1 folded — instruction 1 / record 0.\n"
        "- Destruction: w1 dry; w2 dry.\n"
        "**Closing:** has not met the bar at walk 2 — one lens still folding.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


# ---------- Thread 63: hyphenated weak-spots ----------


def test_63_hyphenated_weakspots_lens_parsed(tmp_path):
    """63: '- Weak-spots: w1 dry' must parse (not drop) the lens line."""
    from cycle_yields import parse_lens_line
    result = parse_lens_line("- Weak-spots: w1 dry")
    assert result is not None, "Hyphenated Weak-spots must not return None"
    assert result[0][0] == "weak-spots"


def test_63_hyphenated_lens_yields_bar_met(tmp_path):
    """63: plan with all lenses using hyphenated Weak-spots → BAR_MET (not CONTINUE from missing lens)."""
    plan = _make_plan(tmp_path,
        "- Weak-spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "- Destruction: w1 dry; w2 dry.\n"
        "**Closing:** ✅ BAR MET — walk 2 dry.\n"
    )
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---- register-enforcement (plan 100029) ----


def test_assert2_invalid_register_warns_verdict_unchanged(tmp_path, monkeypatch):
    """Test 7 — assert #2 on a plan whose register is invalid (NO_TABLE) emits a WARN
    via the warnings collector but does NOT change the verdict. Warn-first: the
    pre-wired FAIL arm at cycle_check.py:424 is deliberately NOT taken here."""
    plan = _make_plan(tmp_path, (
        "**Walk register:** walk-register-test.md\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "**Closing:** BAR MET\n"
    ))
    reg = tmp_path / "walk-register-test.md"
    reg.write_text(
        "# Walk Register\n\n**schema_version:** `0.3`\n\nNo tables.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)

    warnings = []
    verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "BAR_MET", f"verdict must be unchanged; got {verdict!r}"
    assert code == 0
    assert len(warnings) > 0, "a WARN must be collected for an invalid register"


def test_assert2_valid_register_no_warn(tmp_path, monkeypatch):
    """Test 8 — assert #2 on a plan whose register is CONFORMANT emits no WARN."""
    plan = _make_plan(tmp_path, (
        "**Walk register:** walk-register-test.md\n"
        "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
        "**Closing:** BAR MET\n"
    ))
    reg = tmp_path / "walk-register-test.md"
    reg.write_text(
        "**schema_version:** `0.3`\n\n"
        "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| f1 | 1 | Weak spots | 1.1 | pre-existing | bad | the bytes | fixed |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)

    warnings = []
    verdict, code = cycle_check.run_check(plan, warnings=warnings)
    assert verdict == "BAR_MET"
    assert code == 0
    assert len(warnings) == 0, "no WARN must be collected for a valid register"


def test_contract_last_stdout_line_is_verdict(tmp_path):
    """Test 9 — contract test (P8): cycle_check's last stdout line is always the bare
    verdict token after the register-enforcement change. Any register WARN must print
    before the verdict or on stderr — not after it."""
    import subprocess
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
        "**Closing:** BAR MET\n"
    ))
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), str(plan)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.stdout.strip(), "cycle_check must emit at least one stdout line"
    last_line = result.stdout.strip().splitlines()[-1].strip()
    assert last_line == "BAR_MET", (
        f"last stdout line must be bare verdict token; got {last_line!r}"
    )


