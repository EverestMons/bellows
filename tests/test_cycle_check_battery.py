"""Tests for cycle_check battery (plan 100041 — thread 117 Ruling 2, shape (a)).

run_battery runs plan_lint, fold_check, and propagation_check on every CONTINUE/BAR_MET
exit. A plan_lint FAIL or fold_check DRIFT withholds the bar; VACUOUS, NO_BASELINE,
and propagation divergences are informational.

Mock discipline: dispatches on the launched script's BASENAME (plan_lint.py,
fold_check.py, propagation_check.py); git reads and everything else pass through to
the real subprocess.run. No real tool runs in these unit tests.
"""

import re
import subprocess
import sys
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = BELLOWS_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib
if "cycle_check" in sys.modules and sys.modules["cycle_check"].__file__ != str(SCRIPTS / "cycle_check.py"):
    del sys.modules["cycle_check"]
import cycle_check

_BAR_MET_DC = (
    "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
    "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
    "- Vulnerabilities: w1 dry; w2 dry.\n"
    "- Integration-record: w1 dry; w2 dry.\n"
    "- ACID: w1 dry; w2 dry.\n"
)

_CONTINUE_DC = (
    "- Weak spots: w1 2 folded — instruction 2 / record 0.\n"
    "- Destruction: w1 dry.\n"
    "- Vulnerabilities: w1 dry.\n"
    "- Integration-record: w1 dry.\n"
    "- ACID: w1 dry.\n"
)

_FULL_VALIDATION = (
    "cycle_check=BAR_MET, plan_lint=0_FAIL, "
    "fold_check=PASS, propagation_check=DIVERGENT:5"
)

_MANIFEST_STANZA = (
    "\n## Cycle Manifest\n"
    "tier: T1\n"
    "target: scripts/cycle_check.py\n"
    "class: shop-infra\n"
    "reads: scripts/cycle_check.py\n"
    "writes: scripts/cycle_check.py\n"
    "open_forks: none\n"
    "walks: 2\n"
    "yields: 2, 0\n"
    f"validation: {_FULL_VALIDATION}\n"
    "coherence: 2/2 walks have register rows\n"
)


def _make_plan(tmp_path, dc_block, filename="plan.md", include_manifest=True):
    plan = tmp_path / filename
    tail = _MANIFEST_STANZA if include_manifest else ""
    plan.write_text(
        f"# Plan\n\n## Drafting Cycle\n{dc_block}\n## End\n{tail}",
        encoding="utf-8",
    )
    return plan


class _MockResult:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _basename_mock(
    lint_rc=0, lint_stdout="",
    fold_rc=0, fold_stdout="FOLD-CHECK CLEAN: machine-readable state unchanged (0 signals held)\n",
    prop_rc=2, prop_stdout="NOT_RUN\n",
    real_run=None,
):
    """Return a subprocess.run mock that dispatches by the launched script's BASENAME.

    plan_lint.py, fold_check.py, propagation_check.py → mocked.
    All other calls (git reads) → pass through to real_run.
    """
    _real = real_run if real_run is not None else subprocess.run

    def mock(cmd, **kw):
        if isinstance(cmd, (list, tuple)) and len(cmd) >= 2:
            basename = Path(str(cmd[1])).name
            if basename == "plan_lint.py":
                return _MockResult(lint_rc, lint_stdout)
            if basename == "fold_check.py":
                return _MockResult(fold_rc, fold_stdout)
            if basename == "propagation_check.py":
                return _MockResult(prop_rc, prop_stdout)
        return _real(cmd, **kw)

    return mock


# ---------------------------------------------------------------------------
# Test 1 — BATTERY line printed BEFORE verdict on every CONTINUE/BAR_MET exit
# ---------------------------------------------------------------------------

_EXIT_FIXTURES = [
    # (dc_block, plan_has_manifest, expected_verdict, description)
    # Exit :498 — T0 BAR_MET (walk-less path, T0 tier with integration result)
    (
        "**cycle_tier:** T0 (no trigger); integration-vs-record pass: PASS\n",
        False,
        "BAR_MET",
        "T0-close",
    ),
    # Exit :513 — walk-less CONTINUE (no walks, not T0)
    (
        "",
        False,
        "CONTINUE",
        "walk-less-continue",
    ),
    # Exit :517 — current_walk == 0
    (
        "- Weak spots: w0 1 folded — instruction 1 / record 0.\n"
        "- Destruction: w0 dry.\n",
        False,
        "CONTINUE",
        "walk0-continue",
    ),
    # Exit :629 — computed BAR_MET
    (
        _BAR_MET_DC,
        True,
        "BAR_MET",
        "computed-bar-met",
    ),
]


@pytest.mark.parametrize(
    "dc_block,include_manifest,expected_verdict,label",
    _EXIT_FIXTURES,
    ids=[f[3] for f in _EXIT_FIXTURES],
)
def test_battery_line_present_before_verdict(
    tmp_path, dc_block, include_manifest, expected_verdict, label
):
    """Test 1 — every CONTINUE/BAR_MET exit appends one BATTERY: line to warnings
    (which main() prints before the verdict). The verdict is not changed by the line.
    Parametrized over all four exits: :498, :513, :517, :629."""
    plan = _make_plan(tmp_path, dc_block, include_manifest=include_manifest)
    mock = _basename_mock(lint_rc=0, lint_stdout="", fold_rc=0, prop_rc=2, prop_stdout="NOT_RUN\n")

    warnings = []
    with patch.object(subprocess, "run", mock):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)

    assert verdict == expected_verdict, f"[{label}] expected {expected_verdict!r}, got {verdict!r}"
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert len(battery_lines) == 1, (
        f"[{label}] expected exactly one BATTERY: line; got {battery_lines!r}\n"
        f"all warnings: {warnings!r}"
    )
    # BATTERY: line must appear BEFORE any WARN: or the verdict (ordering guaranteed
    # by main() printing warnings before verdict; here we just verify it's in warnings)
    assert battery_lines[0].startswith("BATTERY: plan_lint="), (
        f"[{label}] BATTERY: line has unexpected shape: {battery_lines[0]!r}"
    )


# ---------------------------------------------------------------------------
# Test 2 — BAR_MET + plan_lint FAIL → CONTINUE, WARN names plan_lint=N_FAIL
# ---------------------------------------------------------------------------

def test_plan_lint_fail_downgrades_bar_met(tmp_path):
    """Test 2 — a plan_lint FAIL withholds the bar and the WARN names the tool and value."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    mock = _basename_mock(
        lint_rc=1, lint_stdout="FAIL: (a) header — plan header parse returned empty\n",
        fold_rc=0, fold_stdout="FOLD-CHECK CLEAN: unchanged\n",
        prop_rc=2, prop_stdout="",
    )

    warnings = []
    with patch.object(subprocess, "run", mock):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)

    assert verdict == "CONTINUE", f"expected CONTINUE after plan_lint FAIL; got {verdict!r}"
    assert code == 0
    warn_strs = [w for w in warnings if "downgraded to CONTINUE" in w]
    assert warn_strs, f"expected a downgrade WARN; warnings={warnings!r}"
    assert "plan_lint=1_FAIL" in warn_strs[0], (
        f"WARN must name plan_lint=N_FAIL; got {warn_strs[0]!r}"
    )


# ---------------------------------------------------------------------------
# Test 3 — BAR_MET + fold_check DRIFT → CONTINUE, WARN names fold_check=DRIFT
#          also: both fire → two WARN lines, plan_lint first
# ---------------------------------------------------------------------------

def test_fold_drift_downgrades_bar_met(tmp_path):
    """Test 3 — a fold_check DRIFT withholds the bar.
    Also covers the both-fire case: two WARN lines, plan_lint's first."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    # Create a beside-plan baseline so fold_check is launched
    baseline = tmp_path / f".{plan.name}.foldcheck.json"
    baseline.write_text('{"_meta": {}}', encoding="utf-8")

    # Both-fire: lint FAIL + fold DRIFT
    mock = _basename_mock(
        lint_rc=1, lint_stdout="FAIL: (a) header\n",
        fold_rc=1, fold_stdout="FOLD-CHECK DRIFT — changed\n",
        prop_rc=2, prop_stdout="",
    )

    warnings = []
    with patch.object(subprocess, "run", mock):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)

    assert verdict == "CONTINUE"
    assert code == 0
    warn_strs = [w for w in warnings if "downgraded to CONTINUE" in w]
    assert len(warn_strs) == 2, (
        f"both-fire case must produce two WARN lines; got {warn_strs!r}"
    )
    assert "plan_lint=" in warn_strs[0], (
        f"plan_lint WARN must be first; got {warn_strs[0]!r}"
    )
    assert "fold_check=DRIFT" in warn_strs[1], (
        f"fold_check WARN must be second; got {warn_strs[1]!r}"
    )

    # Single-fire: fold DRIFT only
    mock_drift_only = _basename_mock(
        lint_rc=0, lint_stdout="",
        fold_rc=1, fold_stdout="FOLD-CHECK DRIFT — changed\n",
        prop_rc=2, prop_stdout="",
    )
    warnings2 = []
    with patch.object(subprocess, "run", mock_drift_only):
        verdict2, _ = cycle_check.run_check(plan, warnings=warnings2)

    assert verdict2 == "CONTINUE"
    warn2 = [w for w in warnings2 if "downgraded to CONTINUE" in w]
    assert len(warn2) == 1
    assert "fold_check=DRIFT" in warn2[0]


# ---------------------------------------------------------------------------
# Test 4 — BAR_MET + fold_check VACUOUS → BAR_MET unaffected
# ---------------------------------------------------------------------------

def test_fold_vacuous_preserves_bar_met(tmp_path):
    """Test 4 — VACUOUS is the expected state at a judged stop (P4a). The bar is unaffected."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    baseline = tmp_path / f".{plan.name}.foldcheck.json"
    baseline.write_text('{"_meta": {}}', encoding="utf-8")

    vacuous_stdout = (
        "FOLD-CHECK VACUOUS: the baseline was taken from THIS exact state "
        "(sha256 abc123…), so it cannot observe a fold.\n"
    )
    mock = _basename_mock(
        lint_rc=0, lint_stdout="",
        fold_rc=2, fold_stdout=vacuous_stdout,
        prop_rc=2, prop_stdout="",
    )

    warnings = []
    with patch.object(subprocess, "run", mock):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)

    assert verdict == "BAR_MET", f"VACUOUS must not downgrade; got {verdict!r}"
    assert code == 0
    downgrade_warns = [w for w in warnings if "downgraded to CONTINUE" in w]
    assert not downgrade_warns, f"no downgrade WARN expected; got {downgrade_warns!r}"
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert any("fold_check=VACUOUS" in b for b in battery_lines), (
        f"BATTERY: line must show fold_check=VACUOUS; got {battery_lines!r}"
    )


# ---------------------------------------------------------------------------
# Test 5 — BAR_MET + no baseline → NO_BASELINE, BAR_MET unaffected
# ---------------------------------------------------------------------------

def test_no_baseline_preserves_bar_met(tmp_path):
    """Test 5 — missing baseline is NOT punished; baseline presence is substrate_check's job."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    # No baseline beside the plan; fold_check must NOT be launched
    tool_calls = {"fold_check": 0}
    real_run = subprocess.run

    def tracking_mock(cmd, **kw):
        if isinstance(cmd, (list, tuple)) and len(cmd) >= 2:
            if Path(str(cmd[1])).name == "fold_check.py":
                tool_calls["fold_check"] += 1
                return _MockResult(0, "FOLD-CHECK CLEAN\n")
            if Path(str(cmd[1])).name == "plan_lint.py":
                return _MockResult(0, "")
            if Path(str(cmd[1])).name == "propagation_check.py":
                return _MockResult(2, "")
        return real_run(cmd, **kw)

    warnings = []
    with patch.object(subprocess, "run", tracking_mock):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)

    assert verdict == "BAR_MET", f"NO_BASELINE must not downgrade; got {verdict!r}"
    assert tool_calls["fold_check"] == 0, "fold_check must not be launched when no baseline"
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert any("fold_check=NO_BASELINE" in b for b in battery_lines), (
        f"BATTERY: line must show fold_check=NO_BASELINE; got {battery_lines!r}"
    )


# ---------------------------------------------------------------------------
# Test 6 — BAR_MET + propagation_check DIVERGENT:N → BAR_MET unaffected
# ---------------------------------------------------------------------------

def test_prop_divergent_preserves_bar_met(tmp_path):
    """Test 6 — propagation divergence is informational (P5); the bar is unaffected."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    mock = _basename_mock(
        lint_rc=0, lint_stdout="",
        fold_rc=0, fold_stdout="FOLD-CHECK CLEAN\n",
        prop_rc=1, prop_stdout="DIVERGENCES: 7\n",
    )

    warnings = []
    with patch.object(subprocess, "run", mock):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)

    assert verdict == "BAR_MET", f"DIVERGENT must not downgrade; got {verdict!r}"
    downgrade_warns = [w for w in warnings if "downgraded to CONTINUE" in w]
    assert not downgrade_warns


# ---------------------------------------------------------------------------
# Test 7 — every ESCALATE exit spawns ZERO battery tool launches
# ---------------------------------------------------------------------------

def _count_battery_calls(plan, monkeypatch=None, extra_setup=None):
    """Run run_check on plan and return the number of battery tool launches."""
    calls = {"n": 0}
    real_run = subprocess.run

    def counting_mock(cmd, **kw):
        if isinstance(cmd, (list, tuple)) and len(cmd) >= 2:
            basename = Path(str(cmd[1])).name
            if basename in ("plan_lint.py", "fold_check.py", "propagation_check.py"):
                calls["n"] += 1
                return _MockResult(0, "")
        return real_run(cmd, **kw)

    if extra_setup:
        extra_setup()

    with patch.object(subprocess, "run", counting_mock):
        cycle_check.run_check(plan, warnings=[])

    return calls["n"]


def test_escalate_exits_spawn_no_battery_tools(tmp_path, monkeypatch):
    """Test 7 — ESCALATE arms are untouched; no battery tool is launched on any arm."""

    # unparseable: multiple DC blocks
    p_unparseable = tmp_path / "unparseable.md"
    p_unparseable.write_text(
        "# P\n\n## Drafting Cycle\n- Weak spots: w1 2 folded.\n\n"
        "## Other\n\n## Drafting Cycle\n- Weak spots: w1 1 folded.\n\n## End\n",
        encoding="utf-8",
    )
    assert _count_battery_calls(p_unparseable) == 0, "unparseable: no battery"

    # assert-fail:1: fold count != instr + rec
    p_af1 = _make_plan(tmp_path, "- Weak spots: w1 3 folded — instruction 2 / record 0.\n",
                       "af1.md", include_manifest=False)
    assert _count_battery_calls(p_af1) == 0, "assert-fail:1: no battery"

    # yield-rising
    p_yr = _make_plan(tmp_path,
                      "- Weak spots: w1 1 folded — instruction 1 / record 0; "
                      "w2 2 folded — instruction 2 / record 0.\n"
                      "- Destruction: w1 dry; w2 dry.\n",
                      "yr.md", include_manifest=False)
    assert _count_battery_calls(p_yr) == 0, "yield-rising: no battery"

    # plateau: 3 consecutive walks with flat counts, no new lens class
    p_plateau = _make_plan(tmp_path,
                           "- Weak spots: w1 1 folded — instruction 1 / record 0; "
                           "w2 dry; w3 dry; w4 dry.\n"
                           "- Destruction: w1 dry; w2 dry; w3 dry; w4 dry.\n"
                           "- Vulnerabilities: w1 dry; w2 dry; w3 dry; w4 dry.\n"
                           "- Integration-record: w1 dry; w2 dry; w3 dry; w4 dry.\n"
                           "- ACID: w1 dry; w2 dry; w3 dry; w4 dry.\n",
                           "plateau.md", include_manifest=False)
    assert _count_battery_calls(p_plateau) == 0, "plateau: no battery"

    # restructuring-fold
    p_restr = _make_plan(tmp_path,
                         "- Weak spots: w1 2 folded — instruction 2 / record 0 "
                         "(restructuring — moved section order).\n",
                         "restr.md", include_manifest=False)
    assert _count_battery_calls(p_restr) == 0, "restructuring-fold: no battery"

    # claimed-close-unmet: claims closure but not dry (CONTINUE before close check)
    p_ccu = _make_plan(tmp_path,
                       "- Weak spots: w1 2 folded — instruction 2 / record 0.\n"
                       "**Closing:** BAR MET\n",
                       "ccu.md", include_manifest=False)
    assert _count_battery_calls(p_ccu) == 0, "claimed-close-unmet: no battery"

    # assert-fail:2: register unresolved (git-dependent — use _find_git_root monkeypatch)
    monkeypatch.setattr(cycle_check, "_find_git_root", lambda _: tmp_path)
    (tmp_path / "path" / "to").mkdir(parents=True, exist_ok=True)
    p_af2 = _make_plan(tmp_path,
                       "**Walk register:** `path/to/missing-register.md`\n"
                       "- Weak spots: w1 2 folded — instruction 2 / record 0.\n",
                       "af2.md", include_manifest=False)
    assert _count_battery_calls(p_af2) == 0, "assert-fail:2: no battery"

    # assert-fail:3: fold happened, git context present, no baseline (git-dependent)
    # The existing test at test_cycle_check.py:108 shows the pattern.
    def mock_git_log(cmd, **kw):
        if isinstance(cmd, (list, tuple)) and len(cmd) >= 2:
            basename = Path(str(cmd[1])).name
            if basename in ("plan_lint.py", "fold_check.py", "propagation_check.py"):
                return _MockResult(0, "")
        # Simulate git log returning a walk commit
        if isinstance(cmd, (list, tuple)) and "log" in cmd:
            return _MockResult(0, "abc123 [draft] w1 fold\n")
        return subprocess.run.__wrapped__(cmd, **kw) if hasattr(subprocess.run, "__wrapped__") else _MockResult(0, "")

    p_af3 = _make_plan(tmp_path,
                       "- Weak spots: w1 2 folded — instruction 2 / record 0.\n",
                       "af3.md", include_manifest=False)
    # Need real git for this — monkeypatch _find_git_root and git log subprocess
    real_run = subprocess.run

    calls_af3 = {"n": 0}

    def af3_mock(cmd, **kw):
        if isinstance(cmd, (list, tuple)) and len(cmd) >= 2:
            basename = Path(str(cmd[1])).name
            if basename in ("plan_lint.py", "fold_check.py", "propagation_check.py"):
                calls_af3["n"] += 1
                return _MockResult(0, "")
        if isinstance(cmd, (list, tuple)) and cmd and "log" in cmd:
            return _MockResult(0, "abc123 [draft] w1 fold\n")
        return real_run(cmd, **kw)

    with patch.object(subprocess, "run", af3_mock):
        verdict_af3, _ = cycle_check.run_check(p_af3, warnings=[])

    assert verdict_af3 == "ESCALATE:assert-fail:3", f"expected assert-fail:3; got {verdict_af3!r}"
    assert calls_af3["n"] == 0, "assert-fail:3: no battery"


# ---------------------------------------------------------------------------
# Test 8 — emit-manifest validation: line keys in correct order, fold_check mapping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "fold_rc,fold_stdout,expected_fold_val",
    [
        (0, "FOLD-CHECK CLEAN: machine-readable state unchanged (1 signals held)\n", "PASS"),
        (1, "FOLD-CHECK DRIFT — changed\n", "DRIFT"),
        (2, "FOLD-CHECK VACUOUS: the baseline was taken from THIS exact state\n", "VACUOUS"),
        (2, "ERROR: no baseline found\n", "NO_BASELINE"),
    ],
    ids=["rc0-PASS", "rc1-DRIFT", "rc2-VACUOUS", "rc2-NO_BASELINE"],
)
def test_emit_manifest_fold_check_mapping(tmp_path, fold_rc, fold_stdout, expected_fold_val):
    """Test 8 — validation: line has four keys in the same order as the pre-change capture;
    fold_check maps rc correctly (thread 190). The key order is cycle_check, plan_lint,
    fold_check, propagation_check — unchanged from the pre-change emission."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    # Baseline beside the plan so fold_check is launched
    baseline = tmp_path / f".{plan.name}.foldcheck.json"
    baseline.write_text('{"_meta": {}}', encoding="utf-8")

    mock = _basename_mock(
        lint_rc=0, lint_stdout="",
        fold_rc=fold_rc, fold_stdout=fold_stdout,
        prop_rc=2, prop_stdout="",
    )

    out = StringIO()
    with patch.object(subprocess, "run", mock):
        with redirect_stdout(out):
            cycle_check.emit_manifest(plan)
    output = out.getvalue()

    m = re.search(r"validation:\s*(.*)", output)
    assert m, f"validation: line not found in emit output:\n{output}"
    val_line = m.group(1)

    # Key order unchanged from pre-change
    expected_keys = ["cycle_check", "plan_lint", "fold_check", "propagation_check"]
    positions = []
    for k in expected_keys:
        idx = val_line.find(k + "=")
        assert idx >= 0, f"key {k!r} not found in validation: line {val_line!r}"
        positions.append(idx)
    assert positions == sorted(positions), (
        f"keys not in expected order; line={val_line!r}"
    )

    # fold_check value
    assert f"fold_check={expected_fold_val}" in val_line, (
        f"expected fold_check={expected_fold_val!r} in {val_line!r}"
    )


# ---------------------------------------------------------------------------
# Test 9 — one implementation: emit_manifest and run_check agree
# ---------------------------------------------------------------------------

def test_one_implementation_emit_and_run_agree(tmp_path):
    """Test 9 — emit_manifest and run_check obtain every tool value from run_battery.
    The value emitted in validation: must equal the value printed in BATTERY:."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    mock = _basename_mock(
        lint_rc=0, lint_stdout="",
        fold_rc=0, fold_stdout="FOLD-CHECK CLEAN: unchanged\n",
        prop_rc=1, prop_stdout="DIVERGENCES: 3\n",
    )

    # run_check BATTERY: line
    warnings = []
    with patch.object(subprocess, "run", mock):
        cycle_check.run_check(plan, warnings=warnings)
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert battery_lines, "run_check must emit a BATTERY: line"
    battery_line = battery_lines[0]

    # emit_manifest validation: line
    out = StringIO()
    with patch.object(subprocess, "run", mock):
        with redirect_stdout(out):
            cycle_check.emit_manifest(plan)
    output = out.getvalue()
    m = re.search(r"validation:\s*(.*)", output)
    assert m, "validation: line not found"
    val_line = m.group(1)

    # Each tool's value must match
    for tool in ("plan_lint", "fold_check", "propagation_check"):
        # Extract from BATTERY: line
        bm = re.search(rf"{tool}=([^\s]+)", battery_line)
        assert bm, f"{tool} not in BATTERY: line {battery_line!r}"
        # Extract from validation: line
        vm = re.search(rf"{tool}=([^,\s]+)", val_line)
        assert vm, f"{tool} not in validation: line {val_line!r}"
        assert bm.group(1) == vm.group(1), (
            f"{tool}: BATTERY: has {bm.group(1)!r}, validation: has {vm.group(1)!r}"
        )


# ---------------------------------------------------------------------------
# Test 10 — baseline resolution order
# ---------------------------------------------------------------------------

def test_baseline_resolution_order(tmp_path):
    """Test 10 — resolve_fold_baseline: manifest fold_baseline: first, beside-plan second.
    A declared-but-unresolvable field → NO_BASELINE even when beside-file exists.

    (a) manifest fold_baseline: declared and resolves → uses manifest path.
    (b) both manifest and beside-file exist → manifest wins.
    (c) declared but unresolvable → NO_BASELINE, beside-file is ignored.
    """
    # (a) Manifest-only: baseline only accessible through fold_baseline:
    baseline_a = tmp_path / "manifest_baseline.foldcheck.json"
    baseline_a.write_text('{"_meta": {}}', encoding="utf-8")

    plan_a = tmp_path / "plan_a.md"
    plan_a.write_text(
        f"# P\n\n## Drafting Cycle\n{_BAR_MET_DC}\n## End\n"
        f"## Cycle Manifest\nfold_baseline: {baseline_a}\n"
        f"validation: {_FULL_VALIDATION}\ncoherence: N/A\n",
        encoding="utf-8",
    )
    path_a, declared_a = cycle_check.resolve_fold_baseline(plan_a)
    assert path_a is not None, "(a) should resolve via manifest"
    assert path_a.resolve() == baseline_a.resolve()
    assert declared_a is True

    # (b) Both: manifest AND beside-plan file → manifest wins
    beside_b = tmp_path / f".plan_b.md.foldcheck.json"
    beside_b.write_text('{"_meta": {}}', encoding="utf-8")
    manifest_b = tmp_path / "manifest_b.foldcheck.json"
    manifest_b.write_text('{"_meta": {}}', encoding="utf-8")

    plan_b = tmp_path / "plan_b.md"
    plan_b.write_text(
        f"# P\n\n## Drafting Cycle\n{_BAR_MET_DC}\n## End\n"
        f"## Cycle Manifest\nfold_baseline: {manifest_b}\n"
        f"validation: {_FULL_VALIDATION}\ncoherence: N/A\n",
        encoding="utf-8",
    )
    path_b, declared_b = cycle_check.resolve_fold_baseline(plan_b)
    assert path_b is not None, "(b) should resolve"
    assert path_b.resolve() == manifest_b.resolve(), (
        "(b) manifest should win over beside-file"
    )

    # (c) Declared but unresolvable → NO_BASELINE, beside-file NOT used
    beside_c = tmp_path / f".plan_c.md.foldcheck.json"
    beside_c.write_text('{"_meta": {}}', encoding="utf-8")

    plan_c = tmp_path / "plan_c.md"
    plan_c.write_text(
        f"# P\n\n## Drafting Cycle\n{_BAR_MET_DC}\n## End\n"
        "## Cycle Manifest\nfold_baseline: /does/not/exist.foldcheck.json\n"
        f"validation: {_FULL_VALIDATION}\ncoherence: N/A\n",
        encoding="utf-8",
    )
    path_c, declared_c = cycle_check.resolve_fold_baseline(plan_c)
    assert path_c is None, "(c) unresolvable declared field must return None"
    assert declared_c is True, "(c) declared must be True even when unresolvable"

    # Verify NO_BASELINE in battery output for (c)
    mock = _basename_mock(lint_rc=0, fold_rc=0, prop_rc=2, prop_stdout="")
    warnings = []
    with patch.object(subprocess, "run", mock):
        verdict, _ = cycle_check.run_check(plan_c, warnings=warnings)

    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert any("fold_check=NO_BASELINE" in b for b in battery_lines), (
        f"(c) BATTERY: line must show NO_BASELINE; got {battery_lines!r}"
    )


# ---------------------------------------------------------------------------
# Test 12 — emit-manifest launches each tool EXACTLY ONCE
# ---------------------------------------------------------------------------

def test_emit_manifest_launches_each_tool_once(tmp_path):
    """Test 12 — the battery= hand-off prevents emit_manifest from launching any tool twice.
    With a beside-plan baseline, all three tools launch and each launches exactly once."""
    plan = _make_plan(tmp_path, _BAR_MET_DC)
    baseline = tmp_path / f".{plan.name}.foldcheck.json"
    baseline.write_text('{"_meta": {}}', encoding="utf-8")

    counts = {"plan_lint.py": 0, "fold_check.py": 0, "propagation_check.py": 0}
    real_run = subprocess.run

    def counting_mock(cmd, **kw):
        if isinstance(cmd, (list, tuple)) and len(cmd) >= 2:
            basename = Path(str(cmd[1])).name
            if basename in counts:
                counts[basename] += 1
                return _MockResult(0, "FOLD-CHECK CLEAN: unchanged (1 signals held)\n" if basename == "fold_check.py" else "")
        return real_run(cmd, **kw)

    out = StringIO()
    with patch.object(subprocess, "run", counting_mock):
        with redirect_stdout(out):
            cycle_check.emit_manifest(plan)

    assert counts["plan_lint.py"] == 1, f"plan_lint launched {counts['plan_lint.py']} times (expected 1)"
    assert counts["fold_check.py"] == 1, f"fold_check launched {counts['fold_check.py']} times (expected 1)"
    assert counts["propagation_check.py"] == 1, (
        f"propagation_check launched {counts['propagation_check.py']} times (expected 1)"
    )


# ---------------------------------------------------------------------------
# Test 13 — one resolver: substrate_status and run_battery name the same baseline
# ---------------------------------------------------------------------------

def test_one_resolver_substrate_and_battery_agree(tmp_path):
    """Test 13 — substrate_status (leg 3) and run_battery use the same resolver.
    On a manifest-only fixture where the baseline is declared via fold_baseline:
    and NOT beside the plan, both resolve the same path."""
    # Baseline at a non-beside-plan path
    baseline = tmp_path / "nonstandard_baseline.foldcheck.json"
    baseline.write_text('{"_meta": {}}', encoding="utf-8")

    plan = tmp_path / "plan.md"
    plan.write_text(
        f"# P\n\n## Drafting Cycle\n{_BAR_MET_DC}\n## End\n"
        f"## Cycle Manifest\nfold_baseline: {baseline}\n"
        f"validation: {_FULL_VALIDATION}\ncoherence: N/A\n",
        encoding="utf-8",
    )

    # Battery resolver
    battery_path, declared = cycle_check.resolve_fold_baseline(plan)
    assert battery_path is not None, "battery resolver must find manifest-declared baseline"
    assert battery_path.resolve() == baseline.resolve()

    # substrate_check resolver (leg 3 calls cycle_check.resolve_fold_baseline after rewrite)
    manifest = cycle_check.parse_manifest_stanza(plan.read_text(encoding="utf-8"))
    substrate_path, _ = cycle_check.resolve_fold_baseline(plan, manifest)
    assert substrate_path is not None, "substrate_check resolver must find same baseline"
    assert substrate_path.resolve() == battery_path.resolve(), (
        "one resolver: substrate_check and battery must name the same path"
    )


# ---------------------------------------------------------------------------
# Test 14 — CONTINUE plan + plan_lint FAIL → BATTERY line, NO downgrade WARN
# ---------------------------------------------------------------------------

def test_continue_plan_lint_fail_no_downgrade_warn(tmp_path):
    """Test 14 — the downgrade exists ONLY at the bar. A CONTINUE plan with a
    plan_lint FAIL gets a BATTERY: line but no 'BAR_MET downgraded' WARN."""
    plan = _make_plan(tmp_path, _CONTINUE_DC)
    mock = _basename_mock(
        lint_rc=1, lint_stdout="FAIL: (a) header\n",
        fold_rc=0, fold_stdout="FOLD-CHECK CLEAN\n",
        prop_rc=2, prop_stdout="",
    )

    warnings = []
    with patch.object(subprocess, "run", mock):
        verdict, code = cycle_check.run_check(plan, warnings=warnings)

    assert verdict == "CONTINUE"
    battery_lines = [w for w in warnings if w.startswith("BATTERY:")]
    assert battery_lines, "CONTINUE plan must still emit a BATTERY: line"
    downgrade_warns = [w for w in warnings if "downgraded to CONTINUE" in w]
    assert not downgrade_warns, (
        f"no downgrade WARN on a CONTINUE plan; got {downgrade_warns!r}"
    )


# ---------------------------------------------------------------------------
# Test 15 — verdict does not depend on call shape
# ---------------------------------------------------------------------------

def test_verdict_independent_of_call_shape(tmp_path):
    """Test 15 — run_check(path), run_check(path, warnings=[]), and the CLI all
    return CONTINUE for a fixture with one plan_lint FAIL. warnings=None must not
    suppress the verdict change (f49)."""
    # Fixture: BAR_MET structure but no plan header → plan_lint FAIL
    plan = _make_plan(tmp_path, _BAR_MET_DC, include_manifest=True)

    mock = _basename_mock(
        lint_rc=1, lint_stdout="FAIL: (a) header — plan header parse returned empty\n",
        fold_rc=0, fold_stdout="FOLD-CHECK CLEAN\n",
        prop_rc=2, prop_stdout="",
    )

    # run_check(path) — no warnings list
    with patch.object(subprocess, "run", mock):
        v1, _ = cycle_check.run_check(plan)

    # run_check(path, warnings=[]) — empty list
    warnings = []
    with patch.object(subprocess, "run", mock):
        v2, _ = cycle_check.run_check(plan, warnings=warnings)

    # CLI — real plan_lint runs; plan has no header → 1 FAIL
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "cycle_check.py"), str(plan)],
        capture_output=True, text=True, timeout=30,
    )
    lines = r.stdout.strip().splitlines()
    v3 = lines[-1] if lines else ""

    assert v1 == "CONTINUE", f"run_check(path) returned {v1!r}, expected CONTINUE"
    assert v2 == "CONTINUE", f"run_check(path, warnings=[]) returned {v2!r}, expected CONTINUE"
    assert v3 == "CONTINUE", f"CLI returned {v3!r} as last line, expected CONTINUE"
