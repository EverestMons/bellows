"""Tests for cycle_check — the drafting-cycle validator.

Every case uses synthetic fixtures in tmp_path. Git-dependent tests
mock subprocess calls to avoid real repo dependencies.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = BELLOWS_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

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
        "**Closing:** CLOSED on walk 1 dry.\n"
    ))
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "ESCALATE:claimed-close-unmet"
    assert code == 1


# ---------- closure false-positive regression ----------


def test_prose_closed_not_false_positive(tmp_path):
    """Mid-cycle block with prose 'closed'/'bar met' but no real closure markers.
    Must NOT trigger claimed-close-unmet (the bug this fix repairs).
    """
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 3 folded — instruction 2 / record 1.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0.\n"
        "Emit-manifest against real closed plans, a closed loop, bar met the criteria.\n"
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
    """THE GUARD MUST SURVIVE: **Closing:** + CLOSED present but walk NOT dry
    (instruction folds remain) → must STILL fire ESCALATE:claimed-close-unmet.
    """
    plan = _make_plan(tmp_path, (
        "- Weak spots: w1 3 folded — instruction 2 / record 1.\n"
        "- Destruction: w1 1 folded — instruction 1 / record 0.\n"
        "**Closing:** walk 1 dry; cycle CLOSED.\n"
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


def test_walk_register_cross_repo(tmp_path, monkeypatch):
    plan = _make_plan(tmp_path, (
        "**Walk register:** `governance/knowledge/research/register.md`\n"
        "- Weak spots: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
    ))
    git_root = tmp_path
    gov = tmp_path / "governance"
    gov.mkdir()
    other_root = tmp_path / "other"

    call_count = [0]
    def mock_find_git_root(path):
        call_count[0] += 1
        resolved = path.resolve() if path.is_dir() else path.parent.resolve()
        if "governance" in str(resolved):
            return other_root
        return git_root

    monkeypatch.setattr(cycle_check, "_find_git_root", mock_find_git_root)
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- closure markers ----------


def test_closure_markers_detected():
    for marker in ["**Closing:** walk 2 dry.", "CLOSED", "CYCLE COMPLETE"]:
        block = f"- Weak spots: w1 1 folded.\n{marker}\n"
        parsed = cycle_check.parse_block(block)
        assert parsed["claims_closure"], f"Failed to detect: {marker}"


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
